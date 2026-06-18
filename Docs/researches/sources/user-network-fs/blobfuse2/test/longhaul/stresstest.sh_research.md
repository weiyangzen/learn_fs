<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/longhaul/stresstest.sh -->
# sources/user-network-fs/blobfuse2/test/longhaul/stresstest.sh

Source path: `sources/user-network-fs/blobfuse2/test/longhaul/stresstest.sh`

## Purpose
GNU parallel stress workload that creates, reads, and deletes many files on a hard-coded blobfuse mount.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: none declared. External commands observed: `parallel`.

## Control Flow
Creates 500 50 MB files from random data with 20-way parallelism, reads each file through `hexdump`, then removes the files. Medium and large profiles are present but commented out.

## State And Persistence
Writes and removes `myfile_small_*` data under `/home/vibhansa/blob_mnt2`.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Hard-coded paths and heavy random-data generation can saturate disk, network, and storage accounts.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/longhaul/stresstest.sh -->
