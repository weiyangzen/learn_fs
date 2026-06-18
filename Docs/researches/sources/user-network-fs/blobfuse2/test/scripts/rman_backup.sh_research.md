<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/rman_backup.sh -->
# sources/user-network-fs/blobfuse2/test/scripts/rman_backup.sh

Source path: `sources/user-network-fs/blobfuse2/test/scripts/rman_backup.sh`

## Purpose
Oracle RMAN backup or backup-simulation workload targeting a blobfuse-mounted backup directory.

## Important APIs, Types, And Functions
Shell functions: `setup_oracle_env`, `cleanup`, `run_sqlplus`, `run_rman`, `install_oracle_xe`, `create_tablespace`, `rman_full_backup`, `rman_incremental_backup`, `rman_backup_and_restore_verify`. Key variables: `MOUNT_POINT`, `DATA_DIR`, `SIZES`, `GREEN`, `RED`, `CYAN`, `NC`, `BACKUP_BASE`, `PASSED`, `FAILED`, `IFS`, `ARCHIVELOG_STATUS`. External commands observed: `blobfuse2`, `wget`, `sqlplus`, `rman`, `yum`.

## Control Flow
Defines setup/cleanup helpers, generates or backs up data at multiple sizes, runs full/incremental/multi-channel backup paths, verifies restore or checksum behavior, and reports pass/fail counters.

## State And Persistence
Mutates backup/source directories, Oracle environment/database state for the real RMAN script, and mounted blobfuse backup storage.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
The real RMAN script can install Oracle XE and operate on database files; hard-coded mount/data locations and privileged package operations make it unsuitable for casual execution.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/rman_backup.sh -->
