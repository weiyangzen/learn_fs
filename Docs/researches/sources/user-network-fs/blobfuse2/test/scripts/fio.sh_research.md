<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/fio.sh -->
# sources/user-network-fs/blobfuse2/test/scripts/fio.sh

Source path: `sources/user-network-fs/blobfuse2/test/scripts/fio.sh`

## Purpose
Performance comparison harness for blobfuse/blobfuse2 workloads.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: `mntPath`, `tmpPath`, `v2configPath`, `v1configPath`, `testname`, `outputPath`, `fiocmd`, `fiocmd`, `fiocmd`, `sed_line`, `blobfuse2_write_average`, `blobfuse2_read_average`, `sed_line`, `blobfuse_write_average`, `blobfuse_read_average`, `blobfuse2_write_average`, `blobfuse2_read_average`, `blobfuse_write_average`, plus 5 more. External commands observed: `blobfuse2`, `blobfuse`, `fusermount3`, `fio`, `ps`.

## Control Flow
The script prepares mount/tmp/output paths, mounts blobfuse variants with supplied configs, runs workload commands such as `fio`, `git clone`, or parallel read/write helpers, parses throughput/IOPS/timing output, writes Markdown-style result tables, and unmounts between runs.

## State And Persistence
Creates output report files, test data in the mount, temp-cache contents, and live FUSE mounts.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Relies on external binaries, fragile text parsing, `sed -i` table mutation, and unguarded cleanup of mount/tmp directories.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/fio.sh -->
