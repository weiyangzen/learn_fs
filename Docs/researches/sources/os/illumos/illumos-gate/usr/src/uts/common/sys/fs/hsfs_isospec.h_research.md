# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/hsfs_isospec.h

This header defines ISO 9660 on-disk layout constants and byte-offset accessor macros.

Integer parsing:
- `ZERO` through `THREE`, `MSB_INT`, `LSB_INT`, `MSB_SHORT`, and `LSB_SHORT` parse multi-byte fields.
- `BOTH_SHORT` and `BOTH_INT` use native direct loads on x86/amd64, but bytewise little-endian extraction on SPARC to avoid unaligned access issues.

Volume descriptor:
- ISO sector size is 2048 bytes, with volume descriptors starting at sector 16.
- Volume descriptor types include boot, primary, supplementary, partition, UNIX extension, and end-of-volume.
- Defines ISO identifier string `"CD001"`, version values, string lengths, and date lengths.
- Provides address and value macros for descriptor fields such as type, standard id/version, system/volume ids, volume size, supplementary escape, set size/sequence, block size, path table locations, root directory, publisher/preparer/application/copyright/abstract/bibliographic ids, timestamps, and file structure version.

Directory records:
- Defines fixed directory-entry sizes and maximum name lengths.
- Provides address/value macros for directory length, XAR length, extent LBN/size, creation date, flags, interleave data, volume set, name length/name, system use area, padding, and SUA length.
- Defines directory flags and prohibited flag combinations.
- Provides date field macros and tests for regular files/directories.

Filename limits:
- ISO v1/v2 and Joliet name length constants are defined, including implementation maxima.

Path table:
- Defines fixed path-table entry size and accessor macros for name length, XAR length, extent LBN, parent number, and name.

Dependencies and relationships:
- Uses macro-based byte offsets instead of C structs to represent unaligned portable disc data.
- Works with HSFS parser code and SUSP/RRIP handling.
