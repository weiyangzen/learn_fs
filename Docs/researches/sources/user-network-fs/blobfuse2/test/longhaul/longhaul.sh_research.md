<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/longhaul/longhaul.sh -->
# sources/user-network-fs/blobfuse2/test/longhaul/longhaul.sh

Source path: `sources/user-network-fs/blobfuse2/test/longhaul/longhaul.sh`

## Purpose
Longhaul watchdog and workload script for continuously validating blobfuse2 with periodic kernel builds.

## Important APIs, Types, And Functions
Shell functions: none declared. Key variables: `SERVICE`, `SCRIPT`, `WORKDIR`. External commands observed: `blobfuse2`, `blobfuse`, `mail`, `top`, `ps`.

## Control Flow
If blobfuse2 is running, a lock file gates one test run that logs memory/elapsed time, removes old mount data, builds a kernel under `/blob_mnt/kernel`, copies logs to the mount, and clears the lock. If blobfuse2 is down, it unmounts/remounts with MSI auth and sends a restart email.

## State And Persistence
Mutates `/blob_mnt`, local logs, `longhaul.lock`, environment variables, and live mount state.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Hard-coded account/client IDs, paths, email address, and broad deletes make this host-specific and unsafe outside the intended longhaul VM.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/longhaul/longhaul.sh -->
