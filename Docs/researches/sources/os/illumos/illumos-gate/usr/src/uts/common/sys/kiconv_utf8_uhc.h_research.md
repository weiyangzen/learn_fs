# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_uhc.h

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-13706, source bytes 262139, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_utf8_uhc_h_cb75ec257b2a_research.md`
- chunk 2: lines 13707-17137, source bytes 65108, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_utf8_uhc_h_569e9a9760fc_research.md`

## Chunk Research

### Chunk 1: lines 1-13706

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_uhc.h lines 1-13706

## Scope

This chunk is in learn_fs subset A because `sources/os/illumos/illumos-gate` is listed in `Docs/research_subset_a.md`. I read the requested source range completely: lines 1-13706 of `usr/src/uts/common/sys/kiconv_utf8_uhc.h`. Adjacent context was used only to confirm that line 13707 continues the same initializer and that the full file later closes the table and guards.

The file is a generated-style illumos kernel Korean code-conversion header. This chunk contains the file prologue, include/C++/kernel guards, the UTF-8-to-UHC table-size macro, and the first 13,625 rows of the `kiconv_utf8_uhc[]` initializer. It ends inside the table body.

## APIs and Data Surface

- Header guard: `_SYS_KICONV_UTF8_UHC_H`.
- C++ wrapper: `extern "C"` around kernel declarations.
- Kernel-only section: all conversion data is under `#ifdef _KERNEL`.
- Macro introduced in this chunk: `KICONV_UTF8_UHC_MAX (17047)`, documented as the maximum number of mappings from UTF-8 to UHC.
- Main object introduced in this chunk: `static kiconv_table_t kiconv_utf8_uhc[] = { ... }`.
- Table element type: `kiconv_table_t` from `sys/kiconv_cck_common.h`, with `uint32_t key` and `uint32_t value`.

Rows are stored as two packed integers, not as `{ ... }` struct initializers:

- `key`: packed UTF-8 byte sequence, such as `0xC2A1` or `0xECAEB5`.
- `value`: packed UHC code, such as `0xA2AE` or `0xA892`.

Verified chunk statistics:

- 13,625 mapping rows in lines 1-13706.
- First row: line 82, `0x0000 -> 0x003F`, the hold entry for non-identical conversion.
- Last row in this chunk: line 13706, `0xECAEB5 -> 0xA892`.
- No duplicate keys or non-ascending keys detected in this chunk.
- Packed UTF-8 key shapes: 1 sentinel row, 170 two-byte UTF-8 keys, and 13,454 three-byte UTF-8 keys.
- 8,118 keys in this chunk fall in the Hangul syllable UTF-8 range.

The early table maps punctuation, symbols, compatibility characters, Greek, Cyrillic, kana, CJK compatibility forms, and Hangul/Jamo-related code points before the large Hangul syllable ranges. The chunk then runs through UHC extension and KS X 1001-style Korean mappings, reaching `0xECAEB5` before the chunk boundary.

## Control Flow

There is no executable control flow in this chunk: no functions, branches, loops, calls, allocation, locking, or error handling. Runtime behavior is entirely data-driven:

1. Shared UTF-8-to-CCK conversion code validates and packs an input UTF-8 character into a `uint32_t` key.
2. Encoding-specific conversion code supplies the `kiconv_utf8_uhc[]` table and `KICONV_UTF8_UHC_MAX`-style count to common lookup logic.
3. Common lookup uses the sorted `kiconv_table_t` array contract, with `kiconv_binsearch(uint32_t key, void *tbl, size_t nitems)` declared in `kiconv_cck_common.h`.
4. On a hit, the packed UHC `value` is emitted by conversion code outside this table; invalid-input, replacement, output-space, and errno behavior live outside this header.

Because lookup depends on sorted keys, the strictly ascending key order in this chunk is a functional invariant, not cosmetic formatting.

## State and Dependencies

All state in this chunk is compile-time static table data. Because the table is `static` in a header, each translation unit that includes it under `_KERNEL` can receive a private copy.

Visible and related dependencies:

- `sys/kiconv_cck_common.h` defines `kiconv_table_t`, declares `kiconv_utf8tocck_t`, `kiconv_binsearch`, `kiconv_utf8_to_cck`, and `kiconvstr_utf8_to_cck`, and owns common UTF-8 validity/replacement integration.
- `sys/kiconv_ko.h` defines UHC byte validity macros: `KICONV_KO_IS_UHC_1st_BYTE` and `KICONV_KO_IS_UHC_2nd_BYTE`.
- `sys/kiconv_uhc_utf8.h` is the reverse-direction companion table with `kiconv_table_array_t kiconv_uhc_utf8[]` and the same full mapping count, `17047`.
- `usr/src/uts/common/sys/Makefile` exports both `kiconv_utf8_uhc.h` and `kiconv_uhc_utf8.h` as system headers.
- `usr/src/uts/common/os/kiconv.c` provides broader kernel iconv registration and invalid/replacement handling, while this header supplies static mapping data.

Repository-wide search of `usr/src` found the specific `kiconv_utf8_uhc` symbol only in this header and export lists, so direct inclusion/selection appears to be generated or build-context dependent rather than visible as a named `.c` include in the searched tree.

## Risks and Invariants

- `KICONV_UTF8_UHC_MAX` must match the complete table length across all chunks. The complete file has 17,047 mapping rows, while this chunk contributes 13,625.
- The table must remain sorted by packed UTF-8 key for binary-search consumers.
- The row count, reverse table, and Korean byte validators must stay consistent; a single wrong packed key/value silently corrupts filename/string conversion.
- The sentinel `0x0000 -> 0x003F` is part of non-identical conversion behavior and should not be treated as a normal Unicode scalar mapping.
- Apparent gaps are expected because not every Unicode scalar maps to UHC and not every byte pair is valid UHC.
- The table is not declared `const`; accidental writes by any including translation unit would mutate its local conversion table.
- The chunk is syntactically incomplete by design: it opens the header and array but does not close the initializer, `_KERNEL`, C++ wrapper, or include guard.

## Cross-Chunk References

- This first chunk owns the prologue, licensing notices, `_SYS_KICONV_UTF8_UHC_H` guard, `_KERNEL` gate, `KICONV_UTF8_UHC_MAX`, and the start of `kiconv_utf8_uhc[]`.
- The chunk ends at line 13706 with `0xECAEB5 -> 0xA892`; line 13707 continues the same table with `0xECAEB6 -> 0xA893`.
- Later chunk(s) must preserve the ascending sequence through the remaining rows, close the `kiconv_utf8_uhc[]` initializer, and close `_KERNEL`, `extern "C"`, and the include guard.
- Per-file merge should reconcile this chunk with the remaining chunk(s), verify the full 17,047-row count against `KICONV_UTF8_UHC_MAX`, and compare high-level consistency with `kiconv_uhc_utf8.h`.

### Chunk 2: lines 13707-17137

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_uhc.h lines 13707-17137

## Scope

This chunk is the final segment of the kernel-only `static kiconv_table_t kiconv_utf8_uhc[]` mapping table declared near line 81. The requested range contains only table entries and the closing preprocessor/C++ guards; it does not define functions, macros, or executable branches.

## APIs And Data

- `kiconv_utf8_uhc[]`: continued UTF-8-to-UHC conversion table. Each row is a `{ key, value }` initializer for `kiconv_table_t`, where `key` is a packed UTF-8 byte sequence and `value` is the corresponding UHC code.
- The visible range starts at `0xECAEB6 -> 0xA893`, continues through late Hangul syllable mappings, then includes compatibility/private-use mappings such as `0xEFA480..0xEFA88B`, fullwidth ASCII/punctuation mappings `0xEFBC81..0xEFBD9E`, and final currency/symbol mappings `0xEFBFA0..0xEFBFA6`.
- The table is closed at line 17129, followed by `#endif /* _KERNEL */`, the `extern "C"` close for C++ inclusion, and the include guard close `_SYS_KICONV_UTF8_UHC_H`.

## Control Flow

There is no local control flow in this chunk. Runtime behavior is data-driven: conversion code elsewhere can binary-search `kiconv_utf8_uhc[]` and emit the `value` for a matched packed UTF-8 `key`. The table is sorted in ascending `key` order across this chunk, which is required by the shared `kiconv_binsearch()` API declared in `kiconv_cck_common.h`.

## State And Dependencies

- State is immutable static initializer data compiled only when `_KERNEL` is defined.
- The element type is `kiconv_table_t`, defined in `kiconv_cck_common.h` as two `uint32_t` fields: `key` and `value`.
- The table size contract is established outside this chunk by `KICONV_UTF8_UHC_MAX (17047)`. This chunk contributes the tail entries to that count.
- Header dependencies include kernel integer typedefs, the common CCK conversion declarations, and inclusion by whatever UHC conversion module instantiates this static table. Because the symbol is `static`, every translation unit that includes the header gets a private copy.

## Risks

- Generated table integrity matters more than local logic: a wrong pair silently corrupts UTF-8 to UHC conversion for that code point.
- Binary search users depend on strict ascending key order. Insertions or edits in this chunk must preserve sort order, including the non-Hangul compatibility ranges near the end.
- The table uses packed UTF-8 byte values rather than Unicode scalar values; maintainers must not normalize entries to code points without changing lookup code.
- The `KICONV_UTF8_UHC_MAX` constant must stay synchronized with the full table length. This final chunk closes the initializer, so omissions or extra rows here affect global bounds used by callers.
- Being a `static` large table in a header can duplicate data if included from multiple translation units, though that appears to be an established illumos kiconv pattern.

## Cross-Chunk References

- Earlier chunks contain the table declaration, license/include guards, `KICONV_UTF8_UHC_MAX`, the first sentinel mapping `0x0000 -> 0x003F`, and the preceding UTF-8/UHC entries.
- This chunk continues directly from line 13706 (`0xECAEB5 -> 0xA892`) and begins at line 13707 (`0xECAEB6 -> 0xA893`), so chunk merging should treat the mapping table as one continuous sorted array.
- The final per-file report should connect this header to the reverse table `kiconv_uhc_utf8.h` and the shared conversion contracts in `kiconv_cck_common.h`, especially `kiconv_table_t`, `kiconv_binsearch()`, `kiconv_utf8_to_cck()`, and `kiconvstr_utf8_to_cck()`.
