<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-setup-swap -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-setup-swap

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-setup-swap_research.md`. Source lines read for this pass: 181.

## Purpose
Root helper that converts existing swap devices to encrypted cryptsetup-backed swap to prevent cleartext private data from leaking through swap.

## Important APIs, Types, And Functions
Shell functions `error`, `info`, `warn`, and `usage`; CLI accepts `-f|--force` and `-n|--no-reload`.

## Control Flow
Requires cryptsetup and root, discovers active swap devices, skips non-swap/RAM/already-encrypted/already-configured swaps, warns about breaking hibernate unless forced, comments out original fstab entries, appends `cryptswapN` entries to `/etc/crypttab` and `/etc/fstab`, then optionally restarts cryptdisks and swaps.

## State And Persistence Behavior
Mutates `/etc/fstab`, `/etc/crypttab`, active swap state, and device mapper mappings.

## Dependencies And Integration Points
Depends on `/proc/swaps`, blkid, dmsetup, sed, cryptsetup, initramfs-tools paths, `/etc/init.d/cryptdisks`, swapoff, and swapon.

## Risks And Edge Cases
System-level configuration edits can break boot, hibernate/resume, or swap availability. It appends entries without transactional rollback.

## Test Signals
Requires VM-level integration tests that inspect fstab/crypttab changes and reboot/swap activation behavior; do not run on shared developer machines.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-setup-swap -->
