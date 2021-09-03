# -*- coding: utf-8 -*-

import boto3
from pathlib_mate import Path


REPO_ROOT = Path(__file__).parent

def deploy_to_local():
    HOME = Path.home()

    for p in Path(REPO_ROOT, "dags").select_by_ext(".py"):
        new_p = Path(HOME, "airflow", "dags", p.basename)
        p.copyto(new_abspath=new_p.abspath, overwrite=True)


def deploy_to_s3(boto_ses, bucket):
    s3_client = boto_ses.client("s3")
    for p in Path(REPO_ROOT, "dags").select_by_ext(".py"):
        s3_client.upload_file(
            p.abspath,
            bucket,
            f"airflow/dags/{p.basename}",
        )


if __name__ == "__main__":
    deploy_to_local()
    boto_ses = boto3.session.Session()
    bucket = "aws-data-lab-sanhe-for-everything"
    deploy_to_s3(boto_ses=boto_ses, bucket=bucket)
