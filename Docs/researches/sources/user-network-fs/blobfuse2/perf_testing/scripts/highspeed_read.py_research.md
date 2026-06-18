<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/perf_testing/scripts/highspeed_read.py -->
# sources/user-network-fs/blobfuse2/perf_testing/scripts/highspeed_read.py

## Purpose
Reads multiple files in parallel using `dd` to `/dev/null` and reports aggregate read throughput.

## Important APIs, Types, and Functions
`copy_file(src)` runs `dd if=<src> of=/dev/null bs=4M status=none`, then returns `os.path.getsize(src)`. `main(file_paths)` maps all input paths through a multiprocessing pool sized to CPU count and prints JSON throughput.

## Control Flow and State
The script expects file paths as command-line arguments. It starts all reads, sums known file sizes, divides by wall-clock time, and emits a JSON result named `read_10_20GB_file`.

## Dependencies and Integration Points
Depends on Python multiprocessing and Unix `dd`. Intended for reading files from Blobfuse2 mounts after creation by related performance scripts.

## Risks and Edge Cases
`Popen` stdout is read, but `dd` writes data to `/dev/null` and status to stderr, so the live byte counter is ineffective. Return code is not checked; `CalledProcessError` is never raised by `Popen` in this form. Failed reads can still count full file size. Very large file lists can spawn many processes.

## Test Signals
The JSON output is a performance estimate. It does not prove data integrity or verify `dd` success.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/perf_testing/scripts/highspeed_read.py -->
