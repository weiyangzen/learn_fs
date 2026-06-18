<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/perf_testing/scripts/fio_bench.sh -->
# sources/user-network-fs/blobfuse2/perf_testing/scripts/fio_bench.sh

## Purpose
Performance harness that mounts Blobfuse2, runs FIO read/write jobs or a custom file-cache read test, captures bandwidth/latency summaries, and records network usage.

## Important APIs, Types, and Functions
Inputs are `<mount_dir> <test_name> <cache_mode>`. `cleanup_mount` unmounts all Blobfuse2 mounts. `mount_blobfuse` clears mount/cache directories and invokes `blobfuse2 mount` with `./config.yaml`. `run_fio_job` drops kernel caches, records `/sys/class/net/$INTERFACE` byte counters, runs `fio`, and emits summary JSON through `jq`. `run_test_suite` remounts per `.fio` file. `run_filecache_read_test` creates a 100GB file, remounts cold, reads with `dd iflag=direct`, and writes JSON summaries.

## Control Flow and State
The script validates arguments, creates an output directory named after the test type, performs an initial cleanup, selects write/read flow, and finally aggregates `*_bandwidth_summary.json` and `*_latency_summary.json` into result arrays. It mutates the mount directory, `/mnt/tempcache`, kernel page cache, and output directories.

## Dependencies and Integration Points
Requires `blobfuse2`, `fio`, `jq`, `bc`, `dd`, `timeout`, `sudo`, Linux `/proc` and `/sys`, and a `config.yaml` in the working directory. It integrates with `perf_testing/config/read` and `perf_testing/config/write` job files.

## Risks and Edge Cases
`set -e` makes failures stop the run, but some cleanup is best-effort. `INTERFACE` is hard-coded to `eth0`, which is wrong on many hosts. The mount cleanup uses `blobfuse2 unmount all`, affecting unrelated mounts. It deletes all contents under the mount directory. File-cache read creates a 100GB object, requiring substantial storage. The positional `cache_mode` is validated only indirectly for the file-cache branch.

## Test Signals
Outputs are FIO JSON files, per-job bandwidth/latency summary JSON, final aggregate JSON, and printed network stats. These are performance signals, not correctness tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/perf_testing/scripts/fio_bench.sh -->
