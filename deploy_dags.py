# -*- coding: utf-8 -*-

"""
Automatically deploy all dags script from
``${dir_project_root}/dags`` to ``${HOME}/airflow/dags``, make them available
in Airflow UI.

This script will perform deployment every 1 seconds to keep them in sync.
"""

import time
import shutil
import hashlib
from pathlib import Path

dir_airflow_dags = Path.home().joinpath("airflow", "dags")
dir_airflow_dags.mkdir(exist_ok=True)

dir_here = Path(__file__).absolute().parent
dir_repo_dags = dir_here.joinpath("dags")


def get_md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def deploy(
    reset: bool = False,
):
    if reset:
        shutil.rmtree(dir_airflow_dags)
        dir_airflow_dags.mkdir()

    for p_src in dir_repo_dags.iterdir():
        if p_src.suffix == ".py":
            p_dst = dir_airflow_dags.joinpath(p_src.name)
            # if file exists, compare md5, if not match, then copy it
            if p_dst.exists():
                if get_md5(p_src) != get_md5(p_dst):
                    print(f"deployed: {p_dst.name}")
                    shutil.copy(p_src, p_dst)
            # if file not exists, just copy it
            else:
                print(f"deployed: {p_dst.name}")
                shutil.copy(p_src, p_dst)


reset = False
# reset = True

ith = 0
while 1:
    ith += 1
    print(f"{ith} th deploy")
    time.sleep(1)
    deploy(reset=reset)
