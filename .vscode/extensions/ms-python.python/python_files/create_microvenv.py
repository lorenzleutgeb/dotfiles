# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import sys;import site;import functools;sys.argv[0] = '/build/extension/python_files/create_microvenv.py';functools.reduce(lambda k, p: site.addsitedir(p, k), ['/nix/store/kpny18sklpigg0gxjwa03nb97i8mggs4-python3.12-debugpy-1.8.14/lib/python3.12/site-packages','/nix/store/xnz6ax2kwn9j3ribwxln7r6bpslr0vi8-python3.12-jedi-language-server-0.45.0/lib/python3.12/site-packages','/nix/store/gfnpq5n7wjwkd3i9cp5v4s0ard0784s0-python3.12-docstring-to-markdown-0.15/lib/python3.12/site-packages','/nix/store/p3a2bkyp8ilks42xn6kzywhxsxwfjbd3-python3.12-jedi-0.19.2/lib/python3.12/site-packages','/nix/store/dn0ql3qh37zyg5n00m8y5vlynvmgga6i-python3.12-parso-0.8.4/lib/python3.12/site-packages','/nix/store/p0mswk21fy7rgzbw2vp8l73j5q0gwczw-python3.12-lsprotocol-2023.0.1/lib/python3.12/site-packages','/nix/store/xgyzhiqjznb9x3l8x8kq0qlj380y5lhz-python3.12-attrs-25.3.0/lib/python3.12/site-packages','/nix/store/dq7ab25cwi5rghyhcxhazi0hkrcd8ras-python3.12-cattrs-24.1.2/lib/python3.12/site-packages','/nix/store/ibf4lz4mh3rkgcc1gdyv7anl1sgarazk-python3.12-pydantic-2.11.1/lib/python3.12/site-packages','/nix/store/8hqz8hwwbzm1zj6hz20dpdcy7f8qfly1-python3.12-annotated-types-0.7.0/lib/python3.12/site-packages','/nix/store/2dwac5hpv1rqgh5qn1my35b77bbyjfyw-python3.12-pydantic-core-2.33.0/lib/python3.12/site-packages','/nix/store/33mich8zlxiyvf6lghbsb7s7yijgy2a7-python3.12-typing-extensions-4.13.0/lib/python3.12/site-packages','/nix/store/z3ab5xdfz69wg9mzipqp3fcnv239c9sa-python3.12-typing-inspection-0.4.0/lib/python3.12/site-packages','/nix/store/ngnlmfsp81si9azlbz8sp5x9kl9xwsnx-python3.12-pygls-1.3.1/lib/python3.12/site-packages','/nix/store/sprv1ldjjlp58ny9wlxhksg0br1vs3gp-python3.12-typeguard-4.4.2/lib/python3.12/site-packages'], site._init_pathinfo());
import argparse
import os
import pathlib
import subprocess
import sys
from typing import Optional, Sequence

VENV_NAME = ".venv"
LIB_ROOT = pathlib.Path(__file__).parent / "lib" / "python"
CWD = pathlib.Path.cwd()


class MicroVenvError(Exception):
    pass


def run_process(args: Sequence[str], error_message: str) -> None:
    try:
        print("Running: " + " ".join(args))
        subprocess.run(args, cwd=os.getcwd(), check=True)  # noqa: PTH109
    except subprocess.CalledProcessError as exc:
        raise MicroVenvError(error_message) from exc


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--name",
        default=VENV_NAME,
        type=str,
        help="Name of the virtual environment.",
        metavar="NAME",
        action="store",
    )
    return parser.parse_args(argv)


def create_microvenv(name: str):
    run_process(
        [sys.executable, os.fspath(LIB_ROOT / "microvenv.py"), name],
        "CREATE_MICROVENV.MICROVENV_FAILED_CREATION",
    )


def main(argv: Optional[Sequence[str]] = None) -> None:
    if argv is None:
        argv = []
    args = parse_args(argv)

    print("CREATE_MICROVENV.CREATING_MICROVENV")
    create_microvenv(args.name)
    print("CREATE_MICROVENV.CREATED_MICROVENV")


if __name__ == "__main__":
    main(sys.argv[1:])
