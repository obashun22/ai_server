"""AI Response Server - Claude AIを使用したTCPベースHTTPサーバー"""

import os
import socket
import logging
import json
import time
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logging.getLogger('httpx').setLevel(logging.WARNING)

anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
if not anthropic_api_key:
    raise ValueError("ANTHROPIC_API_KEY not set")

client = Anthropic(api_key=anthropic_api_key)


def parse_request_line(raw_request: str) -> tuple[str, str]:
    """HTTPリクエストラインを解析してメソッドとパスを抽出"""
    lines = raw_request.split('\n')
    if lines:
        parts = lines[0].strip().split()
        if len(parts) >= 2:
            return parts[0], parts[1]
    return "UNKNOWN", "/"


def build_error_response(error: Exception) -> tuple[str, int, int]:
    """500エラーレスポンスを構築"""
    error_body = json.dumps({
        "error": f"Internal Server Error: {str(error)}",
        "status": "error"
    })
    error_bytes = error_body.encode('utf-8')
    response = f"HTTP/1.1 500 Internal Server Error\nContent-Type: application/json\nContent-Length: {len(error_bytes)}\nConnection: close\n\n{error_body}"
    return response, 500, len(error_bytes)


def process_with_ai(raw_request: str) -> tuple[str, int, int]:
    """Claude AIでHTTPリクエストを処理してレスポンスを返す"""
    try:
        system_prompt = """You are an HTTP server AI. Generate a complete HTTP response.

Rules:
- Follow HTTP format strictly: status line, headers, blank line, body
- Include Content-Type and Connection: close headers
- Do NOT include Content-Length header (calculated later)
- Return ONLY the HTTP response, no markdown code blocks or explanations

Example:
HTTP/1.1 200 OK
Content-Type: application/json
Connection: close

{"message": "Hello, World!"}"""

        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": f"Process this HTTP request:\n\n```\n{raw_request}\n```"}]
        )

        ai_response = message.content[0].text.strip()

        if '\r\n\r\n' in ai_response:
            header_part, body = ai_response.split('\r\n\r\n', 1)
            line_sep = '\r\n'
        elif '\n\n' in ai_response:
            header_part, body = ai_response.split('\n\n', 1)
            line_sep = '\n'
        else:
            raise ValueError("Invalid HTTP format")

        body_bytes = body.encode('utf-8')
        content_length = len(body_bytes)
        http_response = f"{header_part}{line_sep}Content-Length: {content_length}{line_sep}{line_sep}{body}"

        status_code = 200
        status_line = header_part.split(line_sep)[0] if line_sep in header_part else header_part.split('\n')[0]
        if 'HTTP/' in status_line:
            parts = status_line.split()
            if len(parts) >= 2:
                try:
                    status_code = int(parts[1])
                except ValueError:
                    pass

        return http_response, status_code, content_length

    except Exception as e:
        logger.error(f"Error: {e}")
        response, status, size = build_error_response(e)
        return response, status, size


def handle_client(client_socket: socket.socket, address: tuple):
    """クライアント接続を処理"""
    start_time = time.time()
    method = "UNKNOWN"
    status_code = 500
    response_size = 0
    path = "/"

    try:
        raw_request = client_socket.recv(4096).decode('utf-8')
        if not raw_request:
            return

        method, path = parse_request_line(raw_request)
        logger.info(f'{address[0]} - - [{time.strftime("%d/%b/%Y:%H:%M:%S +0000", time.gmtime())}] "{method} {path} HTTP/1.1" - - "-" "-" - Request received')

        http_response, status_code, response_size = process_with_ai(raw_request)
        client_socket.sendall(http_response.encode('utf-8'))

        elapsed = time.time() - start_time
        logger.info(f'{address[0]} - - [{time.strftime("%d/%b/%Y:%H:%M:%S +0000", time.gmtime())}] "{method} {path} HTTP/1.1" {status_code} {response_size} "-" "-" {elapsed:.3f}s')

    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f'{address[0]} - - [{time.strftime("%d/%b/%Y:%H:%M:%S +0000", time.gmtime())}] "{method} {path} HTTP/1.1" 500 0 "-" "-" {elapsed:.3f}s Error: {e}')
    finally:
        client_socket.close()


def start_server(host: str = '0.0.0.0', port: int = 8000):
    """TCPサーバーを起動"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((host, port))
        server_socket.listen(5)
        logger.info(f"Server started on {host}:{port}")

        while True:
            client_socket, address = server_socket.accept()
            handle_client(client_socket, address)

    except KeyboardInterrupt:
        logger.info("Server shutting down...")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        server_socket.close()
        logger.info("Server stopped")


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    start_server(host, port)
