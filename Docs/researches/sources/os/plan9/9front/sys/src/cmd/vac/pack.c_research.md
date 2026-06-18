# File Research: sources/os/plan9/9front/sys/src/cmd/vac/pack.c

Purpose: Owns the on-disk/in-Venti metadata block, metadata entry, and `VacDir` binary formats.

Key behavior:
- Provides big-endian integer get/put macros for 8/16/32/48/64-bit fields.
- Packs and unpacks counted strings used in directory entries.
- `mbunpack`/`mbpack` validate and emit `MetaBlock` headers, including `MetaMagic+1` compatibility through `unbotch`.
- `meunpack`, `mecmp`, and `mecmpnew` validate entries and compare names for binary search.
- `mbdelete`, `mbinsert`, `mballoc`, `mbcompact`, and `mbresize` maintain index slots and variable-sized entry payloads.
- `vdsize`, `vdpack`, and `vdunpack` serialize `VacDir` fields, version-specific generation fields, Plan 9 metadata, qid-space annotations, and legacy version 7 replacement-score skipping.
- `vdcleanup` and `vdcopy` manage `VacDir` string ownership.
- `mbsearch` performs binary search inside one metadata block and returns either a found entry or an insertion index.

Dependencies:
- Uses `vac.h` constants (`MetaMagic`, `DirMagic`, option tags), `dat.h` structs, Venti allocation helpers, and Vac error strings.

Notable details:
- Metadata offsets and sizes are 16-bit, so metadata blocks must stay below that practical limit.
- Version 9 stores `gen`, `mentry`, and `mgen` in the fixed part; version 8 uses optional generation metadata.
