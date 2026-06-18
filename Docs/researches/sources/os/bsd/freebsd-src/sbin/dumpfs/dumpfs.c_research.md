# File Research: sources/os/bsd/freebsd-src/sbin/dumpfs/dumpfs.c

Implements `dumpfs`, a UFS superblock and cylinder-group inspection tool.

Key responsibilities:
- Opens each supplied filesystem/device using `libufs`.
- Finds the UFS superblock with `sbfind()`.
- Prints either filesystem ID, free-space list, reconstructable `newfs` command, superblock only, or full superblock plus cylinder groups.

Options:
- `-f`: print free block ranges; repeated `-ff` prints each free block individually.
- `-m`: marshal filesystem parameters into a `newfs` command.
- `-l`: print UFS ID path under `/dev/ufsid`.
- `-s`: print superblock only, skipping cylinder groups.

Important functions:
- `dumpfsid()` prints `/dev/ufsid/<fs_id>`.
- `dumpfs()` prints UFS1/UFS2 superblock fields, flags, check-hash flags, summary counters, and cylinder groups.
- `dumpcg()` prints per-cylinder-group metadata and bitmaps.
- `dumpfreespace()` / `dumpfreespacecg()` list free fragments.
- `marshal()` emits a `newfs` command approximating the existing filesystem.
- `pbits()` prints set-bit ranges.
- `pblklist()` prints free block ranges or individual blocks.
- `ufserr()` normalizes `libufs` and `errno` errors.

UFS details:
- Distinguishes UFS1 and UFS2 field layouts.
- Reports modern flags including soft updates, SUJ, ACL variants, TRIM, gjournal, indexed directories, and metadata check hashes.
- Uses `cgread()` to iterate cylinder groups through `libufs`.

Risks and constraints:
- Output is human-readable and stable enough for diagnostics, not a structured API.
- `marshal()` intentionally leaves some `newfs` options unimplemented.
- Some printed values are legacy UFS1-only fields and are conditional on `disk.d_ufs`.
