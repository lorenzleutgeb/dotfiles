import sys;import site;import functools;sys.argv[0] = '/build/extension/python_files/tensorboard_launcher.py';functools.reduce(lambda k, p: site.addsitedir(p, k), ['/nix/store/kpny18sklpigg0gxjwa03nb97i8mggs4-python3.12-debugpy-1.8.14/lib/python3.12/site-packages','/nix/store/xnz6ax2kwn9j3ribwxln7r6bpslr0vi8-python3.12-jedi-language-server-0.45.0/lib/python3.12/site-packages','/nix/store/gfnpq5n7wjwkd3i9cp5v4s0ard0784s0-python3.12-docstring-to-markdown-0.15/lib/python3.12/site-packages','/nix/store/p3a2bkyp8ilks42xn6kzywhxsxwfjbd3-python3.12-jedi-0.19.2/lib/python3.12/site-packages','/nix/store/dn0ql3qh37zyg5n00m8y5vlynvmgga6i-python3.12-parso-0.8.4/lib/python3.12/site-packages','/nix/store/p0mswk21fy7rgzbw2vp8l73j5q0gwczw-python3.12-lsprotocol-2023.0.1/lib/python3.12/site-packages','/nix/store/xgyzhiqjznb9x3l8x8kq0qlj380y5lhz-python3.12-attrs-25.3.0/lib/python3.12/site-packages','/nix/store/dq7ab25cwi5rghyhcxhazi0hkrcd8ras-python3.12-cattrs-24.1.2/lib/python3.12/site-packages','/nix/store/ibf4lz4mh3rkgcc1gdyv7anl1sgarazk-python3.12-pydantic-2.11.1/lib/python3.12/site-packages','/nix/store/8hqz8hwwbzm1zj6hz20dpdcy7f8qfly1-python3.12-annotated-types-0.7.0/lib/python3.12/site-packages','/nix/store/2dwac5hpv1rqgh5qn1my35b77bbyjfyw-python3.12-pydantic-core-2.33.0/lib/python3.12/site-packages','/nix/store/33mich8zlxiyvf6lghbsb7s7yijgy2a7-python3.12-typing-extensions-4.13.0/lib/python3.12/site-packages','/nix/store/z3ab5xdfz69wg9mzipqp3fcnv239c9sa-python3.12-typing-inspection-0.4.0/lib/python3.12/site-packages','/nix/store/ngnlmfsp81si9azlbz8sp5x9kl9xwsnx-python3.12-pygls-1.3.1/lib/python3.12/site-packages','/nix/store/sprv1ldjjlp58ny9wlxhksg0br1vs3gp-python3.12-typeguard-4.4.2/lib/python3.12/site-packages'], site._init_pathinfo());
import contextlib
import mimetypes
import os
import sys
import time

from tensorboard import program


def main(logdir):
    # Environment variable for PyTorch profiler TensorBoard plugin
    # to detect when it's running inside VS Code
    os.environ["VSCODE_TENSORBOARD_LAUNCH"] = "1"

    # Work around incorrectly configured MIME types on Windows
    mimetypes.add_type("application/javascript", ".js")

    # Start TensorBoard using their Python API
    tb = program.TensorBoard()
    tb.configure(bind_all=False, logdir=logdir)
    url = tb.launch()
    sys.stdout.write(f"TensorBoard started at {url}\n")
    sys.stdout.flush()

    with contextlib.suppress(KeyboardInterrupt):
        while True:
            time.sleep(60)
    sys.stdout.write("TensorBoard is shutting down")
    sys.stdout.flush()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        logdir = str(sys.argv[1])
        sys.stdout.write(f"Starting TensorBoard with logdir {logdir}")
        main(logdir)
