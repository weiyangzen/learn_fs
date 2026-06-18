<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/read_cache/run_read_cache_fio_workload.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/read_cache/run_read_cache_fio_workload.sh

## Purpose
Runs epoch-based fio read or random-read workload against a prepared read-cache mount.

## Important APIs, Types, And Functions
Shell entry point with positional arguments and local helper functions where defined.

## Control Flow
Validates workload dir, `WORKING_DIR`, and read type; drops caches; primes metadata cache with `ls -R`; then loops epochs running fio with environment variables and drops page cache between epochs.

## State And Persistence Behavior
Mutates kernel caches via `/proc/sys/vm/drop_caches`, prints memory stats, and executes fio from the repo job file.

## Dependencies
Depends on sudo, fio, `free`, valid `WORKING_DIR`, and `job_files/read_cache_load_test.fio`.

## Integration Points
Part of the GCSFuse perfmetrics automation under the same source tree.

## Risks And Edge Cases
Requires root privileges for cache dropping; `workload_dir` can be unset if `-d` is omitted; typo in read-type error text is harmless.

## Test Signals
No direct tests in this subset unless invoked by a higher-level Kokoro or wrapper job.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/read_cache/run_read_cache_fio_workload.sh -->
