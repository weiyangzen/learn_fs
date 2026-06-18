# File Research: sources/os/plan9/plan9/sys/src/cmd/vac/pack.c

Purpose: binary packing and unpacking of Vac metadata blocks, metadata entries, and `VacDir` records.

Key structures and helpers:
- `MetaChunk` tracks free/used regions inside a metablock during allocation and compaction.
- Big-endian integer macros encode/decode 8-, 16-, 32-, 48-, and 64-bit fields.
- `stringunpack` and `stringpack` encode strings as 16-bit length plus bytes.

Metablock behavior:
- `mbunpack` validates magic, size, index counts, and handles `MetaMagic+1` via `unbotch`.
- `mbpack` writes metablock headers.
- `meunpack` validates index offsets and embedded directory entry magic.
- `mecmp` and `mecmpnew` compare entry names for binary search; `mbsearch` chooses comparison based on `unbotch`.
- `mballoc` finds holes, appends, or compacts with `metachunks`/`mbcompact`.
- `mbinsert`, `mbdelete`, and `mbresize` maintain sorted index entries and free-space accounting.

VacDir behavior:
- `vdsize` computes packed length for version 8 or 9 records.
- `vdpack` serializes fixed fields, strings, and optional Plan 9/qidspace/generation sections.
- `vdunpack` supports versions 7 through 9, including older replacement-score fields and optional metadata sections.
- `vdcleanup` and `vdcopy` manage the heap-owned strings in `VacDir`.

Integration points:
- `file.c` relies on this code for all directory lookup, enumeration, creation, rename, remove, and root initialization.
- Format constants are declared in `vac.h` and versions in `fns.h`.

Risks:
- This is format-critical code with manual pointer arithmetic and 16-bit offsets; malformed metadata can corrupt assumptions if validation is weakened.
- `metachunks` has dense consistency logic around offsets/free space; changes require careful fixture coverage.
- `vdunpack` allocates strings and must always be paired with `vdcleanup` by callers.
