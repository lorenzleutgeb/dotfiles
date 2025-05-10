import sys;import site;import functools;sys.argv[0] = '/build/extension/python_files/python_server.py';functools.reduce(lambda k, p: site.addsitedir(p, k), ['/nix/store/kpny18sklpigg0gxjwa03nb97i8mggs4-python3.12-debugpy-1.8.14/lib/python3.12/site-packages','/nix/store/xnz6ax2kwn9j3ribwxln7r6bpslr0vi8-python3.12-jedi-language-server-0.45.0/lib/python3.12/site-packages','/nix/store/gfnpq5n7wjwkd3i9cp5v4s0ard0784s0-python3.12-docstring-to-markdown-0.15/lib/python3.12/site-packages','/nix/store/p3a2bkyp8ilks42xn6kzywhxsxwfjbd3-python3.12-jedi-0.19.2/lib/python3.12/site-packages','/nix/store/dn0ql3qh37zyg5n00m8y5vlynvmgga6i-python3.12-parso-0.8.4/lib/python3.12/site-packages','/nix/store/p0mswk21fy7rgzbw2vp8l73j5q0gwczw-python3.12-lsprotocol-2023.0.1/lib/python3.12/site-packages','/nix/store/xgyzhiqjznb9x3l8x8kq0qlj380y5lhz-python3.12-attrs-25.3.0/lib/python3.12/site-packages','/nix/store/dq7ab25cwi5rghyhcxhazi0hkrcd8ras-python3.12-cattrs-24.1.2/lib/python3.12/site-packages','/nix/store/ibf4lz4mh3rkgcc1gdyv7anl1sgarazk-python3.12-pydantic-2.11.1/lib/python3.12/site-packages','/nix/store/8hqz8hwwbzm1zj6hz20dpdcy7f8qfly1-python3.12-annotated-types-0.7.0/lib/python3.12/site-packages','/nix/store/2dwac5hpv1rqgh5qn1my35b77bbyjfyw-python3.12-pydantic-core-2.33.0/lib/python3.12/site-packages','/nix/store/33mich8zlxiyvf6lghbsb7s7yijgy2a7-python3.12-typing-extensions-4.13.0/lib/python3.12/site-packages','/nix/store/z3ab5xdfz69wg9mzipqp3fcnv239c9sa-python3.12-typing-inspection-0.4.0/lib/python3.12/site-packages','/nix/store/ngnlmfsp81si9azlbz8sp5x9kl9xwsnx-python3.12-pygls-1.3.1/lib/python3.12/site-packages','/nix/store/sprv1ldjjlp58ny9wlxhksg0br1vs3gp-python3.12-typeguard-4.4.2/lib/python3.12/site-packages'], site._init_pathinfo());
import ast
import contextlib
import io
import json
import sys
import traceback
import uuid
from typing import Dict, List, Optional, Union

STDIN = sys.stdin
STDOUT = sys.stdout
STDERR = sys.stderr
USER_GLOBALS = {}


def _send_message(msg: str):
    # Content-Length is the data size in bytes.
    length_msg = len(msg.encode())
    STDOUT.buffer.write(f"Content-Length: {length_msg}\r\n\r\n{msg}".encode())
    STDOUT.buffer.flush()


def send_message(**kwargs):
    _send_message(json.dumps({"jsonrpc": "2.0", **kwargs}))


def print_log(msg: str):
    send_message(method="log", params=msg)


def send_response(
    response: str,
    response_id: int,
    execution_status: bool = True,  # noqa: FBT001, FBT002
):
    send_message(
        id=response_id,
        result={"status": execution_status, "output": response},
    )


def send_request(params: Optional[Union[List, Dict]] = None):
    request_id = uuid.uuid4().hex
    if params is None:
        send_message(id=request_id, method="input")
    else:
        send_message(id=request_id, method="input", params=params)

    return request_id


original_input = input


def custom_input(prompt=""):
    try:
        send_request({"prompt": prompt})
        headers = get_headers()
        # Content-Length is the data size in bytes.
        content_length = int(headers.get("Content-Length", 0))

        if content_length:
            message_text = STDIN.buffer.read(content_length).decode()
            message_json = json.loads(message_text)
            return message_json["result"]["userInput"]
    except Exception:
        print_log(traceback.format_exc())


# Set input to our custom input
USER_GLOBALS["input"] = custom_input
input = custom_input  # noqa: A001


def handle_response(request_id):
    while not STDIN.closed:
        try:
            headers = get_headers()
            # Content-Length is the data size in bytes.
            content_length = int(headers.get("Content-Length", 0))

            if content_length:
                message_text = STDIN.buffer.read(content_length).decode()
                message_json = json.loads(message_text)
                our_user_input = message_json["result"]["userInput"]
                if message_json["id"] == request_id:
                    send_response(our_user_input, message_json["id"])
                elif message_json["method"] == "exit":
                    sys.exit(0)

        except Exception:  # noqa: PERF203
            print_log(traceback.format_exc())


def exec_function(user_input):
    try:
        compile(user_input, "<stdin>", "eval")
    except SyntaxError:
        return exec
    return eval


def check_valid_command(request):
    try:
        user_input = request["params"]
        ast.parse(user_input[0])
        send_response("True", request["id"])
    except SyntaxError:
        send_response("False", request["id"])


def execute(request, user_globals):
    str_output = CustomIO("<stdout>", encoding="utf-8")
    str_error = CustomIO("<stderr>", encoding="utf-8")
    str_input = CustomIO("<stdin>", encoding="utf-8", newline="\n")

    with contextlib.redirect_stdout(str_output), contextlib.redirect_stderr(str_error):
        original_stdin = sys.stdin
        try:
            sys.stdin = str_input
            execution_status = exec_user_input(request["params"], user_globals)
        finally:
            sys.stdin = original_stdin

    send_response(str_output.get_value(), request["id"], execution_status)


def exec_user_input(user_input, user_globals) -> bool:
    user_input = user_input[0] if isinstance(user_input, list) else user_input

    try:
        callable_ = exec_function(user_input)
        retval = callable_(user_input, user_globals)
        if retval is not None:
            print(retval)
        return True
    except KeyboardInterrupt:
        print(traceback.format_exc())
        return False
    except Exception:
        print(traceback.format_exc())
        return False


class CustomIO(io.TextIOWrapper):
    """Custom stream object to replace stdio."""

    def __init__(self, name, encoding="utf-8", newline=None):
        self._buffer = io.BytesIO()
        self._custom_name = name
        super().__init__(self._buffer, encoding=encoding, newline=newline)

    def close(self):
        """Provide this close method which is used by some tools."""
        # This is intentionally empty.

    def get_value(self) -> str:
        """Returns value from the buffer as string."""
        self.seek(0)
        return self.read()


def get_headers():
    headers = {}
    while True:
        line = STDIN.buffer.readline().decode().strip()
        if not line:
            break
        name, value = line.split(":", 1)
        headers[name] = value.strip()
    return headers


if __name__ == "__main__":
    while not STDIN.closed:
        try:
            headers = get_headers()
            # Content-Length is the data size in bytes.
            content_length = int(headers.get("Content-Length", 0))

            if content_length:
                request_text = STDIN.buffer.read(content_length).decode()
                request_json = json.loads(request_text)
                if request_json["method"] == "execute":
                    execute(request_json, USER_GLOBALS)
                if request_json["method"] == "check_valid_command":
                    check_valid_command(request_json)
                elif request_json["method"] == "exit":
                    sys.exit(0)

        except Exception:  # noqa: PERF203
            print_log(traceback.format_exc())
