<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/ai/master_mount.sh -->
# sources/user-network-fs/blobfuse2/test/ai/master_mount.sh

## Purpose
Mounts a Blobfuse2 container in read-write mode for storing and accessing AI model data.

## Important APIs, Types, and Functions
Exports Azure storage account and MSI auth variables, prepares `/mnt/blobfuse/mnt`, `/mnt/blobfuse/cache`, and `/mnt/ramdisk`, installs Python ML packages, unmounts prior mount, creates a 200G tmpfs, and runs `blobfuse2 mount` with block cache and base logging.

## Control Flow and State
The script mutates system mounts, installs pip packages, clears the mount path, and starts Blobfuse2. It leaves the mount active.

## Dependencies and Integration Points
Requires Blobfuse2, Azure MSI access, sudo, tmpfs capacity, pip, transformers, torch, and a container named `vibhansa`.

## Risks and Edge Cases
Hard-coded account/container/path values. It deletes contents under `$MOUNT_PATH` after mounting or before use depending on current mount state, which can be destructive. It installs packages globally in the active Python environment.

## Test Signals
Successful mount and accessible `/mnt/blobfuse/mnt` are primary signals; logs go to `master_blobfuse2.log`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/ai/master_mount.sh -->
