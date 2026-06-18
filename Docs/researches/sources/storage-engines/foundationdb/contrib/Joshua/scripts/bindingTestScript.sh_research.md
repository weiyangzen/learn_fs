# sources/storage-engines/foundationdb/contrib/Joshua/scripts/bindingTestScript.sh

## Purpose
Main legacy Joshua binding tester runner that starts a local cluster, runs binding tests, and saves diagnostics on failure.

## Important APIs, Types, and Functions
Uses `localClusterStart.sh` functions such as `startCluster`, `stopCluster`, and `displayMessage`; configures `BINDIR`, `LIBDIR`, `PYTHONDIR`, `testScript`, `SAVEONERROR`, and `VERSION`.

## Control Flow and Integration
After argument validation it starts a cluster, traps exit to stop it, runs `tests/bindingtester/run_binding_tester.sh` with `PYTHONPATH`, `LD_LIBRARY_PATH`, `FDB_CLUSTER_FILE`, console logging, and cycle count. On failure it captures directory listings, processes, cluster file, severity-40 logs, netstat, disk, and environment.

## State and Persistence
Depends on package-local binaries, Python bindings, binding tester shell script, local cluster script, grep/netstat/df/ps, and LD_LIBRARY_PATH behavior.

## Dependencies
Runtime state includes cluster files/logs from `localClusterStart.sh`, console log, error logs, and optional diagnostics under `LOGDIR`.

## Risks and Test Signals
Risks include shell word-splitting from unquoted source, Linux-centric diagnostics, and cleanup only if `stopCluster` succeeds. Test signal is exit status plus captured logs and severity errors.
