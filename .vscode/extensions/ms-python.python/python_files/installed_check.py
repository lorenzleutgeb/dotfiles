# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import sys;import site;import functools;sys.argv[0] = '/build/extension/python_files/installed_check.py';functools.reduce(lambda k, p: site.addsitedir(p, k), ['/nix/store/kpny18sklpigg0gxjwa03nb97i8mggs4-python3.12-debugpy-1.8.14/lib/python3.12/site-packages','/nix/store/xnz6ax2kwn9j3ribwxln7r6bpslr0vi8-python3.12-jedi-language-server-0.45.0/lib/python3.12/site-packages','/nix/store/gfnpq5n7wjwkd3i9cp5v4s0ard0784s0-python3.12-docstring-to-markdown-0.15/lib/python3.12/site-packages','/nix/store/p3a2bkyp8ilks42xn6kzywhxsxwfjbd3-python3.12-jedi-0.19.2/lib/python3.12/site-packages','/nix/store/dn0ql3qh37zyg5n00m8y5vlynvmgga6i-python3.12-parso-0.8.4/lib/python3.12/site-packages','/nix/store/p0mswk21fy7rgzbw2vp8l73j5q0gwczw-python3.12-lsprotocol-2023.0.1/lib/python3.12/site-packages','/nix/store/xgyzhiqjznb9x3l8x8kq0qlj380y5lhz-python3.12-attrs-25.3.0/lib/python3.12/site-packages','/nix/store/dq7ab25cwi5rghyhcxhazi0hkrcd8ras-python3.12-cattrs-24.1.2/lib/python3.12/site-packages','/nix/store/ibf4lz4mh3rkgcc1gdyv7anl1sgarazk-python3.12-pydantic-2.11.1/lib/python3.12/site-packages','/nix/store/8hqz8hwwbzm1zj6hz20dpdcy7f8qfly1-python3.12-annotated-types-0.7.0/lib/python3.12/site-packages','/nix/store/2dwac5hpv1rqgh5qn1my35b77bbyjfyw-python3.12-pydantic-core-2.33.0/lib/python3.12/site-packages','/nix/store/33mich8zlxiyvf6lghbsb7s7yijgy2a7-python3.12-typing-extensions-4.13.0/lib/python3.12/site-packages','/nix/store/z3ab5xdfz69wg9mzipqp3fcnv239c9sa-python3.12-typing-inspection-0.4.0/lib/python3.12/site-packages','/nix/store/ngnlmfsp81si9azlbz8sp5x9kl9xwsnx-python3.12-pygls-1.3.1/lib/python3.12/site-packages','/nix/store/sprv1ldjjlp58ny9wlxhksg0br1vs3gp-python3.12-typeguard-4.4.2/lib/python3.12/site-packages'], site._init_pathinfo());
import argparse
import json
import os
import pathlib
import sys
from typing import Dict, List, Optional, Sequence, Tuple, Union

LIB_ROOT = pathlib.Path(__file__).parent / "lib" / "python"
sys.path.insert(0, os.fspath(LIB_ROOT))

import tomli  # noqa: E402
from importlib_metadata import metadata  # noqa: E402
from packaging.requirements import Requirement  # noqa: E402

DEFAULT_SEVERITY = "3"  # 'Hint'
try:
    SEVERITY = int(os.getenv("VSCODE_MISSING_PGK_SEVERITY", DEFAULT_SEVERITY))
except ValueError:
    SEVERITY = int(DEFAULT_SEVERITY)


def parse_args(argv: Optional[Sequence[str]] = None):
    if argv is None:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Check for installed packages against requirements"
    )
    parser.add_argument("FILEPATH", type=str, help="Path to requirements.[txt, in]")

    return parser.parse_args(argv)


def parse_requirements(line: str) -> Optional[Requirement]:
    try:
        req = Requirement(line.strip("\\"))
        if req.marker is None or req.marker.evaluate():
            return req
    except Exception:
        pass
    return None


def process_requirements(req_file: pathlib.Path) -> List[Dict[str, Union[str, int]]]:
    diagnostics = []
    for n, line in enumerate(req_file.read_text(encoding="utf-8").splitlines()):
        if line.startswith(("#", "-", " ")) or line == "":
            continue

        req = parse_requirements(line)
        if req:
            try:
                # Check if package is installed
                metadata(req.name)
            except Exception:
                diagnostics.append(
                    {
                        "line": n,
                        "character": 0,
                        "endLine": n,
                        "endCharacter": len(req.name),
                        "package": req.name,
                        "code": "not-installed",
                        "severity": SEVERITY,
                    }
                )
    return diagnostics


def get_pos(lines: List[str], text: str) -> Tuple[int, int, int, int]:
    for n, line in enumerate(lines):
        index = line.find(text)
        if index >= 0:
            return n, index, n, index + len(text)
    return (0, 0, 0, 0)


def process_pyproject(req_file: pathlib.Path) -> List[Dict[str, Union[str, int]]]:
    diagnostics = []
    try:
        raw_text = req_file.read_text(encoding="utf-8")
        pyproject = tomli.loads(raw_text)
    except Exception:
        return diagnostics

    lines = raw_text.splitlines()
    reqs = pyproject.get("project", {}).get("dependencies", [])
    for raw_req in reqs:
        req = parse_requirements(raw_req)
        n, start, _, end = get_pos(lines, raw_req)
        if req:
            try:
                # Check if package is installed
                metadata(req.name)
            except Exception:
                diagnostics.append(
                    {
                        "line": n,
                        "character": start,
                        "endLine": n,
                        "endCharacter": end,
                        "package": req.name,
                        "code": "not-installed",
                        "severity": SEVERITY,
                    }
                )
    return diagnostics


def get_diagnostics(req_file: pathlib.Path) -> List[Dict[str, Union[str, int]]]:
    diagnostics = []
    if not req_file.exists():
        return diagnostics

    if req_file.name == "pyproject.toml":
        diagnostics = process_pyproject(req_file)
    else:
        diagnostics = process_requirements(req_file)

    return diagnostics


def main():
    args = parse_args()
    diagnostics = get_diagnostics(pathlib.Path(args.FILEPATH))
    print(json.dumps(diagnostics, ensure_ascii=False))


if __name__ == "__main__":
    main()
