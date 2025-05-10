# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import sys;import site;import functools;sys.argv[0] = '/build/extension/python_files/create_conda.py';functools.reduce(lambda k, p: site.addsitedir(p, k), ['/nix/store/kpny18sklpigg0gxjwa03nb97i8mggs4-python3.12-debugpy-1.8.14/lib/python3.12/site-packages','/nix/store/xnz6ax2kwn9j3ribwxln7r6bpslr0vi8-python3.12-jedi-language-server-0.45.0/lib/python3.12/site-packages','/nix/store/gfnpq5n7wjwkd3i9cp5v4s0ard0784s0-python3.12-docstring-to-markdown-0.15/lib/python3.12/site-packages','/nix/store/p3a2bkyp8ilks42xn6kzywhxsxwfjbd3-python3.12-jedi-0.19.2/lib/python3.12/site-packages','/nix/store/dn0ql3qh37zyg5n00m8y5vlynvmgga6i-python3.12-parso-0.8.4/lib/python3.12/site-packages','/nix/store/p0mswk21fy7rgzbw2vp8l73j5q0gwczw-python3.12-lsprotocol-2023.0.1/lib/python3.12/site-packages','/nix/store/xgyzhiqjznb9x3l8x8kq0qlj380y5lhz-python3.12-attrs-25.3.0/lib/python3.12/site-packages','/nix/store/dq7ab25cwi5rghyhcxhazi0hkrcd8ras-python3.12-cattrs-24.1.2/lib/python3.12/site-packages','/nix/store/ibf4lz4mh3rkgcc1gdyv7anl1sgarazk-python3.12-pydantic-2.11.1/lib/python3.12/site-packages','/nix/store/8hqz8hwwbzm1zj6hz20dpdcy7f8qfly1-python3.12-annotated-types-0.7.0/lib/python3.12/site-packages','/nix/store/2dwac5hpv1rqgh5qn1my35b77bbyjfyw-python3.12-pydantic-core-2.33.0/lib/python3.12/site-packages','/nix/store/33mich8zlxiyvf6lghbsb7s7yijgy2a7-python3.12-typing-extensions-4.13.0/lib/python3.12/site-packages','/nix/store/z3ab5xdfz69wg9mzipqp3fcnv239c9sa-python3.12-typing-inspection-0.4.0/lib/python3.12/site-packages','/nix/store/ngnlmfsp81si9azlbz8sp5x9kl9xwsnx-python3.12-pygls-1.3.1/lib/python3.12/site-packages','/nix/store/sprv1ldjjlp58ny9wlxhksg0br1vs3gp-python3.12-typeguard-4.4.2/lib/python3.12/site-packages'], site._init_pathinfo());
import argparse
import os
import pathlib
import subprocess
import sys
from typing import Optional, Sequence, Union

CONDA_ENV_NAME = ".conda"
CWD = pathlib.Path.cwd()


class VenvError(Exception):
    pass


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--python",
        action="store",
        help="Python version to install in the virtual environment.",
        default=f"{sys.version_info.major}.{sys.version_info.minor}",
    )
    parser.add_argument(
        "--install",
        action="store_true",
        default=False,
        help="Install packages into the virtual environment.",
    )
    parser.add_argument(
        "--git-ignore",
        action="store_true",
        default=False,
        help="Add .gitignore to the newly created virtual environment.",
    )
    parser.add_argument(
        "--name",
        default=CONDA_ENV_NAME,
        type=str,
        help="Name of the virtual environment.",
        metavar="NAME",
        action="store",
    )
    return parser.parse_args(argv)


def file_exists(path: Union[str, pathlib.PurePath]) -> bool:
    return os.path.exists(path)  # noqa: PTH110


def conda_env_exists(name: Union[str, pathlib.PurePath]) -> bool:
    return os.path.exists(CWD / name)  # noqa: PTH110


def run_process(args: Sequence[str], error_message: str) -> None:
    try:
        print("Running: " + " ".join(args))
        subprocess.run(args, cwd=os.getcwd(), check=True)  # noqa: PTH109
    except subprocess.CalledProcessError as exc:
        raise VenvError(error_message) from exc


def get_conda_env_path(name: str) -> str:
    return os.fspath(CWD / name)


def install_packages(env_path: str) -> None:
    yml = os.fspath(CWD / "environment.yml")
    if file_exists(yml):
        print(f"CONDA_INSTALLING_YML: {yml}")
        run_process(
            [
                sys.executable,
                "-m",
                "conda",
                "env",
                "update",
                "--prefix",
                env_path,
                "--file",
                yml,
            ],
            "CREATE_CONDA.FAILED_INSTALL_YML",
        )
        print("CREATE_CONDA.INSTALLED_YML")


def add_gitignore(name: str) -> None:
    git_ignore = CWD / name / ".gitignore"
    if not git_ignore.is_file():
        print(f"Creating: {os.fsdecode(git_ignore)}")
        git_ignore.write_text("*")


def main(argv: Optional[Sequence[str]] = None) -> None:
    if argv is None:
        argv = []
    args = parse_args(argv)

    if conda_env_exists(args.name):
        env_path = get_conda_env_path(args.name)
        print(f"EXISTING_CONDA_ENV:{env_path}")
    else:
        run_process(
            [
                sys.executable,
                "-m",
                "conda",
                "create",
                "--yes",
                "--prefix",
                args.name,
                f"python={args.python}",
            ],
            "CREATE_CONDA.ENV_FAILED_CREATION",
        )
        env_path = get_conda_env_path(args.name)
        print(f"CREATED_CONDA_ENV:{env_path}")
        if args.git_ignore:
            add_gitignore(args.name)

    if args.install:
        install_packages(env_path)


if __name__ == "__main__":
    main(sys.argv[1:])
