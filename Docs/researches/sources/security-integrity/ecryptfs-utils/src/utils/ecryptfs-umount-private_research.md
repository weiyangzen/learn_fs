<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-umount-private -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-umount-private

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-umount-private_research.md`. Source lines read for this pass: 26.

## Purpose
Shell wrapper that unmounts the user's private directory and removes corresponding FEK/FNEK keys from the user keyring.

## Important APIs, Types, And Functions
Uses `/sbin/umount.ecryptfs_private`, `~/.ecryptfs/Private.sig`, `keyctl list @u`, and `keyctl unlink`.

## Control Flow
Detects whether `$PWD` is the private mount, invokes the setuid unmount helper, then iterates signatures in `Private.sig` and unlinks matching user keys. It prints a current-shell refresh hint if relevant.

## State And Persistence Behavior
Changes mount state and keyring state; reads per-user signature file.

## Dependencies And Integration Points
Depends on grep, keyctl, awk, gettext, and the private unmount helper.

## Risks And Edge Cases
Signature matching by grep suffix can unlink unexpected matching keys if key descriptions collide. Missing signature files can make key cleanup incomplete.

## Test Signals
Mount a private directory, run wrapper, confirm `/proc/mounts` no longer lists it and `keyctl list @u` no longer contains its signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-umount-private -->
