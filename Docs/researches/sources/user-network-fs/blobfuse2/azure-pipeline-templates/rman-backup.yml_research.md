# sources/user-network-fs/blobfuse2/azure-pipeline-templates/rman-backup.yml

## Purpose
This template runs actual Oracle RMAN backup workloads against a Blobfuse2 mount to validate database backup behavior and integrity.

## Important APIs, Types, and Functions
It generates cache-mode-specific configs, mounts through `mount.yml` with `-o allow_other`, edits `/etc/fuse.conf` to enable `user_allow_other`, and runs `test/scripts/rman_backup.sh $(MOUNT_DIR) $(ROOT_DIR) 10M,100M,1G,10G`.

## Control Flow
The template creates the config, mounts Blobfuse2 after enabling FUSE `allow_other` so the `oracle` user can access the mount, runs the RMAN script for multiple database file sizes, and prints logs/traces on failure.

## State and Persistence Behavior
It mutates `/etc/fuse.conf`, writes real RMAN backup data to the mounted container, and depends on Oracle XE state on the agent.

## Dependencies and Integration Points
It is used by nightly `RmanBackupTests` on Oracle Linux and requires Oracle XE availability or installation by the script.

## Risks and Edge Cases
System-level FUSE config is modified. The test is long and environment-specific. Block-cache RMAN paths are disabled in the nightly pipeline due to known issues, indicating risk around that mode.

## Test Signals
Signals include successful Oracle RMAN script completion for all sizes, no permission errors from `allow_other`, and no integrity failures in logs.
