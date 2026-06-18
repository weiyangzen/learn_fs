# File Research: sources/os/bsd/netbsd-src/sys/fs/cd9660/iso_rrip.h

Read completely: 85 lines.

Defines RRIP/SUSP analysis bit flags used by `cd9660_rrip.c`. Flags identify parsed or requested fields such as attributes, device numbers, symlinks, alternate names, child/parent links, relocated directories, timestamps, RR flags, extension references, continuations, offsets, stop records, and unknown fields.

Defines `ISO_RRIP_ANALYZE`, the shared state object passed through RRIP parser callbacks. It carries the target inode, wanted fields mask, continuation location, mount pointer, output inode number pointer, output buffer and length tracking, max length, and continuation state for multi-record symlink/name assembly.

The header exports the four RRIP entry points used by the rest of cd9660: analyze inode metadata, get alternate name, get symlink target, and detect RRIP offset.
