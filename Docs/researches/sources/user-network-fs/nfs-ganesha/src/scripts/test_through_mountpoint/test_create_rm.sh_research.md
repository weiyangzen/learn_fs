<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_create_rm.sh -->
# sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_create_rm.sh

## Purpose
This mountpoint smoke test stresses repeated create, remove, rename, list, and remove sequences on one temporary directory. It is intended to expose stale cache and operation ordering issues for simple file lifecycle operations.

## Important APIs, Types, and Functions
The script uses `TEST_DIR`, `SUB_DIR1=touch_rm-$$`, two long filename constants, `NB_LOOP=100`, and an `ERR` counter. It invokes `touch`, `rm`, `mv`, `ls -li`, `ls -l`, and `rm -rf`.

## Control Flow
After setup, the first loop alternates `touch` and `rm` for each of two filenames. The second loop creates `FILENAME_1`, renames it to `FILENAME_2`, and removes it. The third loop adds an intervening `ls -l` before the rename/remove. Each failed operation increments `ERR` and prints diagnostics. The test directory is removed at the end.

## State and Persistence Behavior
All created files are transient within `touch_rm-$$`. There is no durable state beyond console output. Early interruption can leave the temporary directory in the mounted export.

## Dependencies and Integration Points
It depends on Bash-style tests/arithmetic and core utilities. It exercises NFS-Ganesha's create, unlink, lookup/getattr through `ls`, rename, and directory cache invalidation paths.

## Risks and Test Signals
Risks include accepting success with nonzero `ERR`, unquoted diagnostic paths in a few commands elsewhere in this test family, and race sensitivity if multiple tests share the same target with colliding names. Test signals are zero errors and server traces showing removed names disappearing before reuse.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_create_rm.sh -->
