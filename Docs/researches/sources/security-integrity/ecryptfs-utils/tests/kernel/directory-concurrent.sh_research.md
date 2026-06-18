<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/directory-concurrent.sh -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/directory-concurrent.sh

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/directory-concurrent.sh_research.md`. Source lines read for this pass: 46.

## Purpose
Kernel regression wrapper that runs the directory-concurrent compiled stress test inside an eCryptfs mount.

## Important APIs, Types, And Functions
Defines `test_cleanup` and uses the shared `tests/lib/etl_funcs.sh` helpers such as `etl_add_keys`, `etl_lmount`, `etl_mount_i`, `etl_create_test_dir`, `etl_umount`, `etl_lumount`, and `etl_unlink_keys`.

## Control Flow
The script sets `rc=1`, sources the ETL helper library, installs a cleanup trap, inserts keys, mounts lower and eCryptfs test filesystems, creates a test directory or file, runs the scenario-specific command or compiled fixture, sets `rc=0` only on the expected behavior, and lets the trap remove mounts, keys, and temporary paths.

## State And Persistence Behavior
Creates temporary lower/upper test directories and files through ETL helpers; changes active mount/keyring state during the test and relies on the trap for cleanup.

## Dependencies And Integration Points
Depends on bash, the eCryptfs kernel module, key insertion helpers, mount helpers, and scenario-specific tools such as `setfacl`, `lsattr`, `truncate`, `dd`, `stat`, `md5sum`, or the paired compiled test.

## Risks And Edge Cases
Tests require privileges and real mounts; failures before the trap or helper bugs can leave mounted filesystems or loaded keys. Several tests intentionally mutate lower encrypted files or fill lower storage.

## Test Signals
The pass condition is mkdir/rmdir race and hang detection; nonzero exit indicates regression, setup failure, timeout, or cleanup-triggered error.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/directory-concurrent.sh -->
