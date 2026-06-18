# File Research: sources/local-fs/udftools/include/ecma_167.h

Packed on-disk structure definitions based on ECMA-167 3rd edition.

Defines core ECMA/UDF building blocks:
- `dchars`, `dstring`, `charspec`, `timestamp`, `regid`.
- Volume Structure Descriptors and standard identifiers.
- Boot descriptors.
- Extent descriptors and descriptor tags.
- Volume descriptor sequence structures: PVD, AVDP, VDP, IUVD, PD, LVD, USD, TD, LVID.
- Partition maps.
- Logical block addresses and short/long/extended allocation descriptors.
- File set descriptors.
- Partition header descriptors.
- File identifier descriptors.
- ICB tags, indirect/terminal entries.
- File entries and extended file entries.
- Extended attribute structures.
- Space bitmap and unallocated space entries.
- Allocation extent flags and file permission constants.

Most structures are marked `packed, may_alias` to match disk layout and tolerate byte-level access.

Key role: authoritative local representation of ECMA-167 disk descriptors used by mkudffs, libudffs, cdrwtool, and related utilities.

No functions or behavior; this is format vocabulary.
