<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_create_ls.sh -->
# sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_create_ls.sh

## Purpose
This mountpoint test creates 100 files in a temporary directory and repeatedly lists the directory, sleeping between reads. It is aimed at readdir stability and visibility of created entries through an NFS-Ganesha mount.

## Important APIs, Types, and Functions
Inputs and variables mirror `test_create.sh`: `TEST_DIR`, `SUB_DIR1=create_ls-$$`, two long filename constants, `NB_ENTREES=100`, and `ERR`. The operational commands are `mkdir -p`, `touch`, `ls`, `sleep 10`, and `rm -rf`.

## Control Flow
The script validates the target directory, creates the subdirectory, creates 100 files with the first filename prefix, then performs 100 `ls "$TEST_DIR/$SUB_DIR1"` calls redirected to `/dev/null`, sleeping ten seconds between calls. It increments `ERR` on create or list failure, removes the test directory, and reports the error count.

## State and Persistence Behavior
Filesystem state is the temporary `create_ls-$$` directory. Runtime duration is intentionally long because of the 100 ten-second sleeps. Cleanup is best-effort at normal script completion.

## Dependencies and Integration Points
It depends on Bash extensions under a `/bin/sh` shebang and standard utilities. It integrates with the mounted export by forcing repeated directory reads after a burst of creates, which can expose server cache, readdir, or stale handle problems.

## Risks and Test Signals
Risks include high wall-clock runtime, no exit-status propagation for `ERR`, and no verification that all expected filenames appear in listings. Test signals are zero reported errors, stable directory listings, and absence of server-side readdir/getattr errors during the sleep-heavy loop.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_create_ls.sh -->
