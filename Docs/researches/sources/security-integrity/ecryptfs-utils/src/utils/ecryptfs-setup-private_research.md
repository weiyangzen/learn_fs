<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-setup-private -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-setup-private

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-setup-private_research.md`. Source lines read for this pass: 464.

## Purpose
Primary setup script for per-user `~/Private` encrypted directories and encrypted-home bootstrap configuration.

## Important APIs, Types, And Functions
Shell functions include `usage`, `undo_msg`, `error`, `error_testing`, `random_passphrase`, and `filename_encryption_available`. CLI controls force, independent wrapping, FNEK, username, login/mount passphrases, automount, bootstrap, and undo instructions.

## Control Flow
Validates user and group membership, resolves home, creates either home-local or `/home/.ecryptfs/$USER` layout, checks for existing config and active mounts, prompts/verifies login and mount passphrases, creates `~/.Private` and mountpoint, writes automount flags and wrapping mode, wraps or temporarily stores the mount passphrase, inserts keys, writes `Private.sig` and `Private.mnt`, then runs a mount/write/umount/read sanity test unless bootstrapping.

## State And Persistence Behavior
Persists `wrapped-passphrase`, `Private.sig`, `Private.mnt`, `auto-mount`, `auto-umount`, `wrapping-independent`, symlinks, and encrypted data directories. Bootstrap may leave `/dev/shm/.ecryptfs-$USER` until PAM wraps it on password setup.

## Dependencies And Integration Points
Depends on unix_chkpwd, libecryptfs command-line tools, `/sbin/mount.ecryptfs_private`, `/sbin/umount.ecryptfs_private`, sysfs version detection, restorecon when present, and standard shell utilities.

## Risks And Edge Cases
This script owns long-lived secret and mount metadata. Argument passphrases are visible to process listings, bootstrap temporarily stores a mount passphrase protected by file mode, and failure handling must keep config files consistent.

## Test Signals
Contains its own mount/write/umount/read checksum test. Additional signals are `ecryptfs-verify`, login automount, logout unmount, and FNEK/no-FNEK setup variants.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-setup-private -->
