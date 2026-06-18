# sources/storage-engines/wiredtiger/test/csuite/random_directio/smoke.sh

Purpose: smoke wrapper for the direct-I/O crash simulation test.

Important APIs, types, and functions: uses POSIX `sh`, `set -e`, `binary_dir` fallback, optional first-argument binary path, `TEST_WRAPPER`, `TEST_THREADS`, `TEST_METHODS`, and constructed `RUN_TEST` commands.

Control flow: resolves `test_random_directio`, sets the smoke matrix to one thread-count value (`5`) and one transaction sync method (`none`), then runs a default fixed-time test and a schema create/drop verbose variant with `-f 20 -S create,drop,verbose`. More exhaustive thread/method and integrated schema variants are present as commented commands.

State and persistence behavior: the wrapper writes no direct state. Each binary run creates direct-I/O work directories and recovered copies, cleaning on success unless preservation options are added manually.

Dependencies and integration points: registered as `EXEC_SCRIPT` for `test_random_directio`; depends on `TEST_WRAPPER`, the built binary, Linux/direct-I/O support, and CMake copying the script beside the binary or passing the binary path.

Risks: the smoke matrix is intentionally reduced; it does not cover `fsync`, `dsync`, tiered storage, or the stronger integrated schema checks. The direct-I/O binary may skip if `O_DIRECT` is unavailable.

Test signals: both smoke invocations must exit zero. Failure in either default or create/drop schema mode indicates crash-copy recovery inconsistency or environment incompatibility.
