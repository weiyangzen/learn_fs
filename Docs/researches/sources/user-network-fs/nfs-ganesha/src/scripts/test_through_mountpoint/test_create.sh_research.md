<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_create.sh -->
# sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_create.sh

## Purpose
This mountpoint smoke test creates 500 files with long names in a temporary subdirectory, renames every file to a second long-name prefix, renames them back, and removes the directory. It targets NFS directory-entry create and rename behavior through a mounted export.

## Important APIs, Types, and Functions
The script takes one argument, `TEST_DIR`, and uses variables `SUB_DIR1`, `FILENAME_1`, `FILENAME_2`, `NB_ENTREES`, and `ERR`. It uses shell arithmetic loops, `touch`, `mv`, `ls -li`, and `rm -rf`.

## Control Flow
After validating that `TEST_DIR` exists, it creates `create_rename-$$`, loops from 0 to 499 creating `FILENAME_1-$I`, loops again renaming each file to `FILENAME_2-$I`, then loops a third time renaming each file back. Each operation increments `ERR` and prints inode diagnostics if it fails. Cleanup removes the subdirectory and prints the total error count.

## State and Persistence Behavior
Temporary state is confined to `$TEST_DIR/create_rename-$$`. The test cleans the subdirectory at the end but does not trap signals or early exits, so interrupted runs can leave files behind.

## Dependencies and Integration Points
It depends on Bash-style `[[ ]]` and `(( ))` syntax despite using `#!/bin/sh`, plus core utilities. It is meant to run against an NFS-Ganesha mounted export and exercise create/rename/remove paths in the server and backing FSAL.

## Risks and Test Signals
Risks include non-portability under strict `/bin/sh`, no nonzero exit on accumulated `ERR`, and destructive `rm -rf` if variables are unexpectedly empty. Test signals are zero reported errors, no leftover subdirectory, and NFS/server logs showing successful CREATE and RENAME sequences under long file names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_create.sh -->
