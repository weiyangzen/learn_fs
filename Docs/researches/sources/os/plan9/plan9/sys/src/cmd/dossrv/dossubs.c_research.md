# File Research: sources/os/plan9/plan9/sys/src/cmd/dossrv/dossubs.c

Core FAT implementation for `dossrv`.

Key behavior:
- Detects FAT boot sectors and parses FAT12/16/32 BPB fields, FAT mirroring flags, root locations, data start, cluster counts, FAT width, and FAT32 info-sector free-space hints.
- Resolves file clusters and sectors, allocating clusters on demand for writes.
- Implements name handling: Plan 9 space/colon translation, DOS 8.3 classification, long-name alias generation, long-name entry parsing/writing, and checksum validation.
- Searches directories, finds free entry ranges for short/long names, reads directories into 9P `Dir` records, and reconstructs parent pointers for `..`.
- Reads, writes, and truncates regular files by walking FAT chains.
- Converts FAT entries to/from Plan 9 `Dir`, including read-only, directory, system/exclusive, and append/contiguous indicators.
- Reads/writes FAT12, FAT16, and FAT32 entries, updates all mirrored FATs, and maintains FAT32 info-sector free counts.
- Allocates clusters, frees chains, and can relocate system files into contiguous extents for `DMAPPEND`.
- Provides time conversion, boot-sector dump helpers, directory-entry dump helpers, case-insensitive comparison, and UTF-to-Rune conversion.

Filesystem relevance:
- This is the real FAT metadata engine: boot parsing, directory walking, long names, FAT chain mutation, allocation, truncation, and contiguity repair.
