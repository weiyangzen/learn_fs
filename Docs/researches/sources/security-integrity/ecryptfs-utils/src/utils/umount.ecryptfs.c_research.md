<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/umount.ecryptfs.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/umount.ecryptfs.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/umount.ecryptfs.c_research.md`. Source lines read for this pass: 190.

## Purpose
General eCryptfs umount helper that unlinks eCryptfs auth tokens from the keyring before delegating to `/bin/umount -i`.

## Important APIs, Types, And Functions
Functions include `get_mount_opt_value`, `unlink_keys_from_keyring`, `construct_umount_args`, and `main`.

## Control Flow
Looks up the target mountpoint in `/etc/mtab`, checks for `ecryptfs_unlink_sigs`, extracts FEK/FNEK signatures from mount options, removes those auth tokens from the keyring, prepends `-i` to the original umount arguments, and `execv`s `/bin/umount`.

## State And Persistence Behavior
Mutates keyring state; actual unmount and mtab updates are delegated to `/bin/umount`.

## Dependencies And Integration Points
Depends on mntent parsing of `/etc/mtab`, libecryptfs key removal, and `/bin/umount`.

## Risks And Edge Cases
Parsing mount options by substring can mis-handle malformed options. Missing mtab entries or no `ecryptfs_unlink_sigs` skip key cleanup.

## Test Signals
Mount with unlink_sigs, unmount through helper, and verify both mount disappearance and key removal. Also test non-eCryptfs arguments are passed to umount.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/umount.ecryptfs.c -->
