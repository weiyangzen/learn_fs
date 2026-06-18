<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/perf_testing/scripts/read.py -->
# sources/user-network-fs/blobfuse2/perf_testing/scripts/read.py

## Purpose
Simple sequential read benchmark for a file named `application_<size>.data` under a mount path.

## Important APIs, Types, and Functions
The script reads CLI args `mountpath` and `size`, opens the file in binary mode, reads 8MiB blocks until `bytes_read <= fileSize`, and prints timing/throughput JSON.

## Control Flow and State
It records open, read, close, and total wall-clock durations. It derives expected file size from integer GB input and accumulates bytes read from returned chunks.

## Dependencies and Integration Points
Uses Python standard libraries and expects the target file to have been created by `write.py` or an equivalent tool on a mounted Blobfuse2 path.

## Risks and Edge Cases
The loop condition `bytes_read <= fileSize` performs one extra read at EOF. If the file is shorter than expected, repeated empty reads can lead to an infinite loop because `bytes_read` stops increasing. There is no argument validation or exception handling.

## Test Signals
JSON output includes open/read/close/total times and MiB/s. It does not check content or guard against short files.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/perf_testing/scripts/read.py -->
