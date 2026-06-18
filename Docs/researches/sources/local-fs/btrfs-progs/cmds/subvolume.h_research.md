# File Research: sources/local-fs/btrfs-progs/cmds/subvolume.h

## Purpose
Small public header for subvolume command formatting metadata.

## Contents
- Include guard `__BTRFS_SUBVOLUME_H__`.
- Forward declares `struct rowspec`.
- Exports `extern const struct rowspec btrfs_subvolume_rowspec[];`.

## Integration
Allows other command code to reuse the subvolume rowspec array without including the large `subvolume.c` implementation.

## Risks
No logic. Compatibility risk is limited to keeping the declaration synchronized with the definition in `cmds/subvolume.c`.
