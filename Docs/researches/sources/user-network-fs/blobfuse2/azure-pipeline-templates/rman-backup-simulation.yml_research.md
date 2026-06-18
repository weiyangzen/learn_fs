# sources/user-network-fs/blobfuse2/azure-pipeline-templates/rman-backup-simulation.yml

## Purpose
This template simulates Oracle RMAN backup workloads on a Blobfuse2 mount to validate database-like file integrity without requiring Oracle XE.

## Important APIs, Types, and Functions
It generates file-cache or block-cache configs, mounts through `mount.yml`, and runs `test/scripts/rman_backup_simulation.sh $(MOUNT_DIR) $(ROOT_DIR) 10M,100M,1G,10G`.

## Control Flow
The template creates a cache-mode-specific config from Azure key templates, mounts Blobfuse2 with `--file-cache-timeout=3200`, runs the simulation script for several database file sizes, and prints logs/traces on failure.

## State and Persistence Behavior
It writes simulated RMAN backup data into the mounted container and uses local root/cache directories. It does not clean up itself beyond caller cleanup.

## Dependencies and Integration Points
It is used by nightly `RmanBackupTests` on Oracle Linux before the real RMAN test.

## Risks and Edge Cases
Large 10G simulations can stress storage capacity and timeouts. The script is external to the template, so integrity guarantees depend on its validation behavior.

## Test Signals
Signals are successful simulation script exit across all sizes and no Blobfuse2 logs/traces indicating write/read failures.
