# File Research: sources/os/bsd/freebsd-src/sys/fs/msdosfs/direntry.h

Defines on-disk FAT directory entries, Win95 long-filename entries, attribute bits, timestamp bitfields, and name conversion prototypes.

Main responsibilities:
- Models the 32-byte DOS short directory entry.
- Models Win95/VFAT long-name subentries.
- Defines directory slot marker values and file attribute bits.
- Defines FAT time/date bit masks and shifts.
- Provides kernel-only interfaces for short-name and long-name conversion.

Key structures and constants:
- `struct direntry`: 8.3 name, attributes, lowercase flags, create/access/modify timestamps, high/low start cluster, and file size.
- Slot markers: `SLOT_EMPTY`, `SLOT_E5`, `SLOT_DELETED`.
- Attributes: readonly, hidden, system, volume, directory, archive, and normal.
- Lowercase flags: `LCASE_BASE`, `LCASE_EXT`.
- `struct winentry`: VFAT LFN sequence count, UTF-16 name parts, `ATTR_WIN95`, checksum, and reserved fields.
- `WIN_CHARS`, `WIN_MAXSUBENTRIES`, and `WIN_MAXLEN` define LFN capacity.

Important dependencies:
- `struct mbnambuf` buffers reconstructed long names in kernel builds.
- Declares conversion helpers implemented in `msdosfs_conv.c`.

Notable risks and edge cases:
- LFN entries are checksum-linked to the following 8.3 entry and must be processed in reverse slot order.
- FAT timestamp fields are packed manually rather than represented with bitfields for portability.
- `WIN_MAXLEN` must fit within `struct dirent.d_name`.
