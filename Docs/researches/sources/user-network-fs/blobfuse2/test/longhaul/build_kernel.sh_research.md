<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/longhaul/build_kernel.sh -->
# sources/user-network-fs/blobfuse2/test/longhaul/build_kernel.sh

Source path: `sources/user-network-fs/blobfuse2/test/longhaul/build_kernel.sh`

## Purpose
Builds a specified Linux kernel version on top of a blobfuse-mounted path to stress long-running compile and filesystem workloads.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: `version`. External commands observed: `git`, `wget`, `make`, `apt`, `apt-get`.

## Control Flow
Installs build dependencies, changes to the supplied mount path, downloads a kernel tarball, extracts it, runs `make defconfig`, and builds with `make`.

## State And Persistence
Creates and mutates a full kernel source tree under the caller-provided path.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Runs package installation and large downloads/builds without `set -e`; partial failures can continue and consume significant mount capacity.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/longhaul/build_kernel.sh -->
