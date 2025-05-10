# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import sys;import site;import functools;sys.argv[0] = '/build/extension/python_files/download_get_pip.py';functools.reduce(lambda k, p: site.addsitedir(p, k), ['/nix/store/kpny18sklpigg0gxjwa03nb97i8mggs4-python3.12-debugpy-1.8.14/lib/python3.12/site-packages','/nix/store/xnz6ax2kwn9j3ribwxln7r6bpslr0vi8-python3.12-jedi-language-server-0.45.0/lib/python3.12/site-packages','/nix/store/gfnpq5n7wjwkd3i9cp5v4s0ard0784s0-python3.12-docstring-to-markdown-0.15/lib/python3.12/site-packages','/nix/store/p3a2bkyp8ilks42xn6kzywhxsxwfjbd3-python3.12-jedi-0.19.2/lib/python3.12/site-packages','/nix/store/dn0ql3qh37zyg5n00m8y5vlynvmgga6i-python3.12-parso-0.8.4/lib/python3.12/site-packages','/nix/store/p0mswk21fy7rgzbw2vp8l73j5q0gwczw-python3.12-lsprotocol-2023.0.1/lib/python3.12/site-packages','/nix/store/xgyzhiqjznb9x3l8x8kq0qlj380y5lhz-python3.12-attrs-25.3.0/lib/python3.12/site-packages','/nix/store/dq7ab25cwi5rghyhcxhazi0hkrcd8ras-python3.12-cattrs-24.1.2/lib/python3.12/site-packages','/nix/store/ibf4lz4mh3rkgcc1gdyv7anl1sgarazk-python3.12-pydantic-2.11.1/lib/python3.12/site-packages','/nix/store/8hqz8hwwbzm1zj6hz20dpdcy7f8qfly1-python3.12-annotated-types-0.7.0/lib/python3.12/site-packages','/nix/store/2dwac5hpv1rqgh5qn1my35b77bbyjfyw-python3.12-pydantic-core-2.33.0/lib/python3.12/site-packages','/nix/store/33mich8zlxiyvf6lghbsb7s7yijgy2a7-python3.12-typing-extensions-4.13.0/lib/python3.12/site-packages','/nix/store/z3ab5xdfz69wg9mzipqp3fcnv239c9sa-python3.12-typing-inspection-0.4.0/lib/python3.12/site-packages','/nix/store/ngnlmfsp81si9azlbz8sp5x9kl9xwsnx-python3.12-pygls-1.3.1/lib/python3.12/site-packages','/nix/store/sprv1ldjjlp58ny9wlxhksg0br1vs3gp-python3.12-typeguard-4.4.2/lib/python3.12/site-packages'], site._init_pathinfo());
import json
import pathlib
import urllib.request as url_lib

from packaging.version import parse as version_parser

EXTENSION_ROOT = pathlib.Path(__file__).parent.parent
GET_PIP_DEST = EXTENSION_ROOT / "python_files"
PIP_PACKAGE = "pip"
PIP_VERSION = "latest"  # Can be "latest", or specific version "23.1.2"


def _get_package_data():
    json_uri = f"https://pypi.org/pypi/{PIP_PACKAGE}/json"
    # Response format: https://warehouse.readthedocs.io/api-reference/json/#project
    # Release metadata format: https://github.com/pypa/interoperability-peps/blob/master/pep-0426-core-metadata.rst
    with url_lib.urlopen(json_uri) as response:
        return json.loads(response.read())


def _download_and_save(root, version):
    root = pathlib.Path.cwd() if root is None or root == "." else pathlib.Path(root)
    url = f"https://raw.githubusercontent.com/pypa/get-pip/{version}/public/get-pip.py"
    print(url)
    with url_lib.urlopen(url) as response:
        data = response.read()
        get_pip_file = root / "get-pip.py"
        get_pip_file.write_bytes(data)


def main(root):
    data = _get_package_data()

    if PIP_VERSION == "latest":
        # Pick latest 5 versions to try and get-pip
        sorted_versions = sorted(data["releases"].keys(), key=version_parser, reverse=True)[:5]
        downloaded = False
        while sorted_versions:
            use_version = sorted_versions.pop(0)
            try:
                print(f"Trying version: get-pip == {use_version}")
                _download_and_save(root, use_version)
                downloaded = True
                break
            except Exception as e:
                print(f"Failed to download get-pip == {use_version}: {e}")
                print(f"NExt attempt(s) with versions: {sorted_versions}")
        if not downloaded:
            raise Exception("Failed to download get-pip.py")
    else:
        use_version = PIP_VERSION
        _download_and_save(root, use_version)


if __name__ == "__main__":
    main(GET_PIP_DEST)
