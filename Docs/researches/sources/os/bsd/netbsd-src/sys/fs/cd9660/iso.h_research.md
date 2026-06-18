# File Research: sources/os/bsd/netbsd-src/sys/fs/cd9660/iso.h

Read completely: 247 lines.

Defines ISO9660 on-disc structures and numeric accessors. The main layouts are `iso_volume_descriptor`, `iso_primary_descriptor`, `iso_supplementary_descriptor`, `iso_directory_record`, and `iso_extended_attributes`, all represented with byte arrays sized by the `ISODCL(from,to)` macro.

The file declares volume descriptor types, standard IDs (`CD001`, `CDW01`), default block size, maximum name length, root directory record layout, and the associated-file prefix `ASSOCCHAR`.

Inline `isonum_*` helpers decode ISO 711/712 one-byte values, 721/722/723 16-bit little/big/both-endian values, and 731/732/733 32-bit little/big/both-endian values. For both-endian fields, the helper chooses the native-endian half at compile time.
