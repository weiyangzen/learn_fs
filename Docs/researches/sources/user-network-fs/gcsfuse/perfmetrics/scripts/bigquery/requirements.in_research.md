# sources/user-network-fs/gcsfuse/perfmetrics/scripts/bigquery/requirements.in

## Purpose

Human-edited dependency input for the BigQuery perfmetrics Python package.

## Important APIs, Types, and Functions

Pins `google-cloud-bigquery==3.11.1`, includes `argparse`, and pins `urllib3==1.26.19`.

## Control Flow

No runtime flow. Dependency tooling compiles this input into a hashed `requirements.txt` consumed by CI.

## State and Persistence Behavior

Influences installed Python environment state only.

## Dependencies and Integration Points

`continuous_test/gcp_ubuntu/build.sh` installs the generated lock file with `pip install --require-hashes`. `google-cloud-bigquery` backs `experiments_gcsfuse_bq.py`.

## Risks and Edge Cases

External `argparse` is unnecessary on modern Python. Stale pins can carry compatibility or security risk. Changes here require regenerating the hashed requirements file to affect Kokoro.

## Test Signals

Successful lock generation, `pip install --require-hashes`, and passing BigQuery unit tests in a clean environment.
