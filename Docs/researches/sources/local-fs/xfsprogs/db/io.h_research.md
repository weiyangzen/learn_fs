# File Research: sources/local-fs/xfsprogs/db/io.h

## Purpose
Defines the IO cursor structures and declares xfs_db cursor, device, write, and verifier helpers.

## Interfaces
- Defines `bbmap_t` as a small discontiguous basic-block map.
- Defines `iocur_t`, including buffer address/length, current typed data pointer, inode context, byte offset, type, optional buffer map, libxfs buffer, and CRC flags.
- Declares cursor globals and manipulation functions.
- Declares device predicates and `iocur_crc_valid()`.

## Dependencies
Couples all xfs_db commands to libxfs buffers, xfs_db type descriptors, and current cursor state.

## Risks And Invariants
`iocur_crc_valid()` returns three states: unchecked `-1`, bad `0`, and good `1`; callers must not treat it as a simple bool without considering unchecked buffers.
