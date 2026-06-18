## sources/security-integrity/ecryptfs-utils/tests/kernel/mmap-close.sh

Purpose: Regression harness for applications that `open`, `mmap`, close the fd, dirty the shared mapping, then `munmap`. It verifies encrypted file data survives unmount/remount by comparing `md5sum` before and after.

Important APIs and functions: shared `etl_*` mount/key helpers, `${test_script_dir}/mmap-close/test`, `md5sum`, `etl_umount`, `etl_mount_i`. Control flow mounts eCryptfs, creates a temp path, lets the C test write via mmap-after-close, hashes the file, remounts, hashes again, and passes if hashes are identical.

State and persistence: Creates an encrypted file whose dirty mmap pages must flush correctly into lower storage. Dependencies include keyring setup, lower/upper mounts, and the sibling C probe. Integration is a kernel test named for Launchpad regressions 870326/1047261. Risks include cache/timing sensitivity; the explicit remount is the persistence boundary and makes stale page-cache-only success less likely.
