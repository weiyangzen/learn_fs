<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/longhaul/telemetrytest.sh -->
# sources/user-network-fs/blobfuse2/test/longhaul/telemetrytest.sh

Source path: `sources/user-network-fs/blobfuse2/test/longhaul/telemetrytest.sh`

## Purpose
Loops through telemetry settings, remounts blobfuse2, and runs the longhaul stress test for each setting.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: none declared. External commands observed: `blobfuse2`.

## Control Flow
For each line in the supplied file, it cleans mount and ramdisk paths, unmounts all blobfuse2 mounts, mounts with `--telemetry=<line>`, logs the pid, runs `stresstest.sh`, then sleeps before the next run.

## State And Persistence
Continuously mutates `~/blob_mnt2`, `/mnt/ramdisk`, blobfuse2 mount state, and `longhaul2.log`.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Infinite outer loop and `rm -rf` on shell-expanded dotfiles require a controlled test host.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/longhaul/telemetrytest.sh -->
