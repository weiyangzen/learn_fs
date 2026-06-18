# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsfix.c

## Role

`ntfsfix.c` implements the `ntfsfix` utility. It is not a full NTFS checker; it performs a limited set of startup and metadata repairs, resets/empties the journal when needed, adjusts dirty state, and schedules Windows `chkdsk` by marking the volume dirty.

## Command-Line Contract

Supported options are:

- `-b/--clear-bad-sectors`: clear `$BadClus::$Bad`.
- `-d/--clear-dirty`: clear the dirty flag after a successful mount/repair path.
- `-n/--no-action`: run read-only and report possible fixes.
- `-h/--help`, `-V/--version`.

There is no real `--force` option in this file. `main()` has a local `force = FALSE`, so it refuses to operate on a read-write mounted device.

## Control Flow

1. `main()` parses options and refuses read-write mounted volumes.
2. It first tries a normal `ntfs_mount()`.
3. If full mount fails, `fix_mount()` allocates a device and calls `ntfs_volume_startup()`.
4. If startup fails, `fix_startup()` replays early startup steps manually and may repair a bad primary boot sector from alternate boot sectors or repair the rare self-located MFT condition.
5. On the fallback repair path, `fix_mount()` runs:
   - `fix_mftmirr()`
   - `fix_upcase()`
   - `set_dirty_flag()`
   - `empty_journal()`
6. After mount succeeds, `main()` always runs `check_alternate_boot()`, then either sets or clears `VOLUME_IS_DIRTY`, optionally clears `$BadClus`, reports NTFS version, and unmounts.

## Major Repair Operations

- `fix_mftmirr()` reads `$MFT` and `$MFTMirr` with MST fixups, validates mirrored records, and writes differing mirror records. If `$MFT` is corrupt and `$MFTMirr` appears valid, it may repair `$MFT` from `$MFTMirr`.
- `fix_upcase()` reads `$UpCase`, checks ASCII case mappings, and rewrites the default upcase table if corrupt and not in no-action mode.
- `check_alternate_boot()` compares primary and alternate boot sectors and rewrites the alternate boot sector when the primary is usable and the filesystem does not overflow the partition.
- `try_alternate_boot()` tries to rebuild the primary boot sector from alternate locations when the primary boot sector cannot parse.
- `fix_self_located_mft()` detects and repairs a rare Windows XP-era corruption where MFT data is described by an MFT record inside the MFT extension itself.
- `clear_badclus()` truncates and reallocates `$BadClus::$Bad` so clusters previously marked bad are unmarked, then clears sparse metadata flags.

## Important Dependencies

The tool directly depends on low-level ntfs-3g volume, device, boot-sector, MFT, runlist, bitmap, logfile, MST, inode, and attribute routines. Several repairs intentionally bypass high-level mount assumptions and use `ntfs_pread()`, `ntfs_pwrite()`, mapping-pair decompression, and raw MFT record writes.

## Risk Areas

- The successful initial mount path does not call `fix_mftmirr()`, `fix_upcase()`, `set_dirty_flag()`, or `empty_journal()`; those run only after startup/mount recovery in `fix_mount()`. The log message on immediate mount success says MFT processing completed even though no comparison was performed there.
- `$MFTMirr` repair has comments warning it does not fully verify that the mirror location is truly correct, especially around software RAID experiments.
- `-d/--clear-dirty` can clear the dirty flag after a successful mount, even though `ntfsfix` normally marks the volume dirty to force Windows checking.
- `-b/--clear-bad-sectors` intentionally frees bad-cluster markings and is dangerous if physical media defects are real.
- Several repairs perform raw sector/MFT writes; interruption during these writes could leave the volume worse.
