# File Research: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/iso_rrip.h

## Scope

Defines RRIP/SUSP analysis flags, parser state, and public RRIP parser entry points.

## APIs And Data Structures

- Defines analysis/result bits for attributes, devices, symlinks, alternate names, child/parent links, relocated directories, timestamps, identifier flags, extension references, continuation records, offsets, stop records, and unknown records.
- `ISO_RRIP_ANALYZE` carries parser input/output state: target node, interesting fields, continuation block/offset/length, mount pointer, optional inode-number output, output buffer, output length, maximum length, and continuation state.
- Declares `cd9660_rrip_analyze()`, `cd9660_rrip_getname()`, `cd9660_rrip_getsymname()`, and `cd9660_rrip_offset()`.

## Dependencies

Kernel-only declarations depend on `struct iso_node`, `struct iso_mnt`, and `struct iso_directory_record`.

## Risks And Invariants

The `fields` bitmask is both a request and progress tracker; handlers clear bits as data is found. Continuation state must be reset and bounded by the parser to avoid following invalid SUSP continuation metadata.
