<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/perf_testing/scripts/write.py -->
# sources/user-network-fs/blobfuse2/perf_testing/scripts/write.py

## Purpose
Simple sequential write benchmark for `application_<size>.data` under a mount path.

## Important APIs, Types, and Functions
The script accepts `mountpath` and integer `size` in GB. It allocates an 8MiB random buffer, writes it repeatedly until the target byte count is exceeded, then prints timing and throughput JSON.

## Control Flow and State
Open, write-loop, close, and total durations are measured separately. The target file remains on disk/mount after completion.

## Dependencies and Integration Points
Uses Python standard libraries. It is commonly paired with `read.py` for Blobfuse2 mount performance.

## Risks and Edge Cases
The loop condition `bytes_written <= fileSize` writes one extra block beyond the requested size. There is no argument validation, fsync, exception handling, or cleanup. `os.urandom(8MiB)` is generated once, so content repeats by block.

## Test Signals
JSON output reports MiB/s and timing breakdown. It does not verify uploaded data or final file size.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/perf_testing/scripts/write.py -->
