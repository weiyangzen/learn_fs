# File Research: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_rrip.c

## Purpose
Implements Rock Ridge Interchange Protocol parsing for cd9660 POSIX metadata, alternate names, symlinks, relocated directories, devices, timestamps, continuation areas, and extension detection.

## Main Elements
- Uses table-driven SUSP/RRIP record scanning via `cd9660_rrip_loop()`.
- Handles `PX` attributes, `TF` timestamps, `PN` device numbers, `RR` field masks, `CE` continuations, `ST` stop records, and `ER` extension references.
- `cd9660_rrip_slink()` builds symlink targets from component records including current, parent, root, volume root, host, and continuation components.
- `cd9660_rrip_altname()` builds Rock Ridge alternate names and supports continuation.
- Default handlers fall back to ISO attributes, timestamps, and transformed ISO names when required RRIP fields are missing.
- `cd9660_rrip_pclink()` handles child/parent relocated directory links.
- `cd9660_rrip_reldir()` hides relocated directory entries from normal lookup by clearing output length/fields.
- `cd9660_rrip_cont()` records continuation block, offset, and length; the loop validates continuation bounds before reading.
- Public entry points: `cd9660_rrip_analyze()`, `cd9660_rrip_getname()`, `cd9660_rrip_getsymname()`, and `cd9660_rrip_offset()`.

## Dependencies And Integration
Works with ISO directory records, cd9660 node defaults, iconv-aware filename conversion, jail-aware hostname retrieval, and buffer-cache reads from the device vnode.

## Risk Notes
Malformed media handling depends on SUSP length/version validation and continuation bounds checks against volume size and logical block size.
