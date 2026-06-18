# sources/storage-engines/wiredtiger/test/live_restore/long_test.sh

Purpose: longer scripted live restore regression suite run from the build directory.

Important behavior: it sources `../test/live_restore/helper.sh` and invokes `run_test` with several `test_live_restore` configurations: 10 iterations with 20k operations and 20 collections, the same with per-directory database mode `-D`, background-thread debug mode `-b -t 1`, crash/death runs with 50k operations and 12 threads, recovery runs with `-r`, and matching per-directory crash/recovery coverage.

Control flow and state: tests run sequentially and stop on helper failure. Death-mode invocations may terminate with exit 137, which helper accepts. Recovery runs rely on state left by preceding death-mode runs.

Dependencies and integration: depends on `helper.sh`, `test/cppsuite/test_live_restore`, and the build-directory relative path layout. It exercises live restore threading, CRUD replay, collection fanout, per-directory database layout, and recovery.

Risks and test signals: the script is intentionally expensive and order-dependent. A failure in a death run can cascade into recovery. Accepted 137 status needs log review to distinguish intended self-kill from resource exhaustion. Strong signals are successful recovery after death-mode runs and completion under both standard and `-D` layouts.
