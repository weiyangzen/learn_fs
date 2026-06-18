# sources/user-network-fs/blobfuse2/azure-pipeline-templates/cleanup.yml

## Purpose
This template unmounts Blobfuse2 mounts and optionally deletes temporary block and ADLS containers.

## Important APIs, Types, and Functions
Parameters are `unmount` and `delete_containers`. It uses `ps`, `df`, `sudo umount -f`, `pidof blobfuse2`, `rm -rf` on mount/cache contents, `/etc/mtab`, and composes `container.yml` for deletion.

## Control Flow
If unmounting is enabled, it prints process/disk state, force unmounts `$(MOUNT_DIR)`, waits, kills Blobfuse2, clears mount and temp directories, and prints mount table under `condition: always()`. If deletion is enabled, it calls `container.yml` twice to delete the generated container from block and ADLS accounts.

## State and Persistence Behavior
It mutates runner mount/cache directories and can delete Azure storage containers named `$(containerName)`.

## Dependencies and Integration Points
It is called before mounts in `mount.yml`, at the end of most test templates, and at the end of top-level pipeline jobs.

## Risks and Edge Cases
`sudo kill -9 \`pidof blobfuse2\`` can kill all Blobfuse2 processes on the agent, which is risky on shared self-hosted runners. `rm -rf $(MOUNT_DIR)/*` can remove mounted contents if unmount failed. Container deletion depends on variables and is Ubuntu-conditioned in `container.yml`.

## Test Signals
Signals include no remaining Blobfuse2 process, no mounted FUSE entry in `df`/`mtab`, empty mount/cache directories, and deleted test containers when requested.
