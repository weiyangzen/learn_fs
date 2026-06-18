# File Research: sources/local-fs/udftools/mkudffs/defaults.h

Declarations for mkudffs default templates.

Exports:
- Default media mapping and sizing tables.
- Descriptor templates for PVD, LVD, IUVD, PD, USD, TD, LVID, sparing table, partition maps, VATs, FSD, FE/EFE, implementation-use extended attributes.
- Default MBR template.

No logic; consumers copy these structures and patch per-filesystem values.
