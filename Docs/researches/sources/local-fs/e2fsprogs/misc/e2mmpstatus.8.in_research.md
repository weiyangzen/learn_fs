# File Research: sources/local-fs/e2fsprogs/misc/e2mmpstatus.8.in

## Purpose
Manual page template for `e2mmpstatus`, the Multiple-Mount Protection status checker for ext4 filesystems.

## Documented Interface
- `e2mmpstatus [-i] file system`
- `-i`: print MMP information instead of checking safety.

## Behavior Described
- Checks whether an MMP-enabled ext4 filesystem is safe to mount.
- Accepts device paths, `UUID=...`, or `LABEL=...`.
- Unsafe conditions include:
  - `e2fsck` running.
  - Filesystem in use by another node.
  - MMP block corrupted or unreadable.
- May wait to observe whether another node is updating the MMP block.

## Exit Codes
- `0`: safe to mount.
- `1`: in use by another node, not safe.
- `2`: other failure preventing reliable status detection.

## Implementation Link
- The implementation is in `dumpe2fs.c`, which switches behavior when invoked as `e2mmpstatus`.
