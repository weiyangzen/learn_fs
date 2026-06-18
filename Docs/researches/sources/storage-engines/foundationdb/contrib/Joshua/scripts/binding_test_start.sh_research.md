# sources/storage-engines/foundationdb/contrib/Joshua/scripts/binding_test_start.sh

## Purpose
Joshua entrypoint for the newer `bindingtester2` package using `contrib/local_cluster` Python tooling.

## Important APIs, Types, and Functions
Runs with `set -e` and `pipefail`, then executes `python3 ./binding_test.py` with fdbserver/fdbcli/libfdb paths, operation counts, concurrency, timeout, random mode, and tees output to `output.log`.

## Control Flow and Integration
Packaged as `joshua_test` by `package_bindingtester2`; it expects to run from the package root containing binaries and `binding_test.py`.

## State and Persistence
Depends on Python3, packaged `binding_test.py`, fdbserver/fdbcli/libfdb, and tee.

## Dependencies
Runtime state is `output.log` and any local-cluster artifacts created by `binding_test.py`.

## Risks and Test Signals
Risks include hard-coded workload sizes/timeouts and package-root assumptions. Test signal is zero exit status from binding_test.py and captured output.log.
