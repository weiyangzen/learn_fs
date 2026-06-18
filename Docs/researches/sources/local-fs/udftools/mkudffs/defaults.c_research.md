# File Research: sources/local-fs/udftools/mkudffs/defaults.c

Static default templates for mkudffs.

Defines:
- `default_media`: maps media type enum values to default sizing/profile groups.
- `default_sizing`: alignment, proportional sizing, and minimum-size rules for VDS, LVID, sparing table, sparing space, and partition space across media classes.
- Default primary volume descriptor.
- Default logical volume descriptor.
- Default implementation-use descriptor payload.
- Default unallocated space descriptor.
- Default terminating descriptor.
- Default logical volume integrity descriptor and implementation-use payload.
- Default sparing table and sparable partition map.
- Default VAT 1.50 and VAT 2.00+ structures.
- Default virtual partition map.
- Default file set descriptor.
- Default file entry and extended file entry.
- Default implementation-use extended attribute.
- Default MBR with one IFS partition entry and boot signature.

Most multi-byte fields are initialized with constant endian-conversion macros so templates are already in on-disk byte order.

Key role: central source of canonical descriptor defaults copied and customized by mkudffs generation code.
