# File Research: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_rrip.h

## Purpose
Defines on-disc Rock Ridge and SUSP record layouts consumed by `cd9660_rrip.c`.

## Main Elements
- Defines `ISO_SUSP_HEADER`.
- Defines RRIP structures for POSIX attributes, device numbers, symlink components, symlinks, alternate names, child/parent links, relocated directories, timestamps, flags, extension references, SP offset, and continuation pointers.
- Defines symlink component flags such as continue, current, parent, root, volume root, and host.
- Defines timestamp format and field flags.
- Defines `ISO_RRIP_SLSIZ`.

## Dependencies And Integration
Layout definitions map directly onto bytes inside ISO system-use areas.

## Risk Notes
Packed on-media layout assumptions are central; callers validate record lengths before using these structures.
