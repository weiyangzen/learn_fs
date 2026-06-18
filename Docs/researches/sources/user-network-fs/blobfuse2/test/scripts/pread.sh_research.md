<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/pread.sh -->
# sources/user-network-fs/blobfuse2/test/scripts/pread.sh

Source path: `sources/user-network-fs/blobfuse2/test/scripts/pread.sh`

## Purpose
File IO helper used by higher-level stress/performance scripts.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: `thread`, `count`, `size`, `mntPath`, `outputPath`, `sed_line`, `start_time`, `end_time`, `time_diff`, `total_size`, `rate`. External commands observed: `parallel`, `dd`.

## Control Flow
The helper performs repeated reads/writes or checksum comparisons with caller-provided size/thread/path parameters, often using GNU parallel or Python threads to increase concurrency.

## State And Persistence
Creates, reads, modifies, or deletes local and mounted test files plus intermediate checksum/result files.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Correctness depends on caller path isolation and consistent cache state; missing quoting and hard-coded paths can redirect writes unexpectedly.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/pread.sh -->
