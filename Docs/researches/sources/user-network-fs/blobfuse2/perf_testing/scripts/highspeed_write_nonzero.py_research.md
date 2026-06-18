<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/perf_testing/scripts/highspeed_write_nonzero.py -->
# sources/user-network-fs/blobfuse2/perf_testing/scripts/highspeed_write_nonzero.py

## Purpose
Copies a nonzero source file into multiple large target files in parallel to measure high-throughput write behavior with realistic data.

## Important APIs, Types, and Functions
`create_file_dd(file_index, folder, source_file, timestamp)` runs `dd if=<source_file> of=<target> bs=1G count=36 oflag=direct`, returning timing and throughput or an error string. `main(folder, num_files, source_file)` creates the folder, runs workers in a multiprocessing pool, and prints human-readable totals.

## Control Flow and State
The script creates timestamped `ddFile_*` outputs, waits for each async worker, filters successful results, and reports total data written, elapsed time, Gbps, and MiB/s. Files persist after completion.

## Dependencies and Integration Points
Depends on Unix `dd`, direct I/O support, Python multiprocessing, and a large readable source file. Used with Blobfuse2 mounted paths to stress upload paths.

## Risks and Edge Cases
Uses `shell=True` with unquoted interpolated paths. `bs=1G` with `oflag=direct` can fail on many systems or consume significant resources. Result tuple shape differs on failure and success, with positional indexing that is easy to break. It does not emit machine-readable JSON unlike related scripts.

## Test Signals
Printed throughput metrics indicate performance only for successful `dd` calls. There is no file-size or checksum validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/perf_testing/scripts/highspeed_write_nonzero.py -->
