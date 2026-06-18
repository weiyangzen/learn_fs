# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_uhc_utf8.h

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-8453, source bytes 262137, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_uhc_utf8_h_f2ac9d54d85e_research.md`
- chunk 2: lines 8454-16909, source bytes 262136, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_uhc_utf8_h_24b0e893478e_research.md`
- chunk 3: lines 16910-17136, source bytes 6848, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_uhc_utf8_h_c1bdf8022969_research.md`

## Chunk Research

### Chunk 1: lines 1-8453

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_uhc_utf8.h lines 1-8453

## Scope

- Repository subset: `Docs/research_subset_a.md`; `sources/os/illumos/illumos-gate` is in scope.
- Source span read completely: lines 1-8453 of `usr/src/uts/common/sys/kiconv_uhc_utf8.h`.
- This is chunk 1 of an oversized generated-style kernel conversion header. It covers the file preamble, guards, exported table-size macro, start of the UHC-to-UTF-8 table, and the first 8,373 table rows.
- The chunk ends inside the `kiconv_uhc_utf8[]` initializer. Line 8453 is key `0xB296`; adjacent line 8454 continues with key `0xB297`, so later chunks own the remaining rows and syntactic closure.

## APIs And Public Surface

- The header is guarded by `_SYS_KICONV_UHC_UTF8_H`, wrapped for C++ with `extern "C"`, and all conversion declarations in this span are gated by `_KERNEL`.
- The only macro defined in this chunk is `KICONV_UHC_UTF8_MAX (17047)`, documented as the maximum mapping number from UHC to UTF-8.
- The primary object introduced here is `static kiconv_table_array_t kiconv_uhc_utf8[] = { ... }`.
- No functions, callbacks, structs, or external symbols are defined. Because the array is `static` in a header, each including translation unit can receive its own private copy.
- The table element type is not defined in this file. It comes from `kiconv_cck_common.h` as a `uint32_t key` plus `uchar_t u8[4]`.

## Data Layout Visible In This Chunk

- Each mapping row uses a UHC code-unit key and a UTF-8 byte initializer in `u8`.
- The first row is a sentinel/fallback-style entry: key `0x0000` maps to `EF BF BD`, with the comment `Hold entry for non-identical conv`.
- Verified chunk statistics for lines 1-8453:
  - 8,373 mapping rows.
  - First key `0x0000`; last key `0xB296`.
  - No duplicate keys and no non-ascending keys in this span.
  - 170 rows have two explicit UTF-8 bytes, from `0xA1A4` through `0xACF1`.
  - 8,203 rows have three explicit UTF-8 bytes.
- The `u8[4]` backing array means omitted initializer bytes are zero-filled. Consumers must use conversion logic that understands UTF-8 length rather than assuming every row has exactly three explicit bytes.
- The early table body maps UHC extension keys beginning at `0x8141` to Hangul UTF-8 syllables. The key order follows UHC lead/trail-byte ordering, including gaps where byte values are not valid UHC trail bytes.
- Around the KS X 1001-compatible ranges, the table includes non-Hangul symbols as well as Hangul: punctuation, mathematical symbols, arrows, fullwidth ASCII forms, jamo, Roman numerals, Greek, box drawing, units, circled characters, hiragana/katakana, Cyrillic, and related compatibility characters. These are the visible source of the two-byte UTF-8 rows in this chunk.
- Near line 8024 the table reaches `0xB041`; near the chunk end it continues through the Hangul run to `0xB296 -> EC BF 80`.

## Control Flow

- There is no executable control flow in this chunk. It is compile-time initializer data plus preprocessor structure.
- Runtime conversion behavior is provided elsewhere by kiconv/CCK conversion code that includes this header and searches or indexes `kiconv_uhc_utf8[]`.
- The data is sorted by key in this span, which is an important invariant for table-driven lookup implementations, especially binary search.

## State And Dependencies

- State is static read-mostly conversion data compiled into kernel code paths that include this header under `_KERNEL`.
- Direct type dependencies visible from surrounding illumos headers:
  - `kiconv_table_array_t` from `kiconv_cck_common.h`.
  - `uint32_t` and `uchar_t` from kernel/common type headers included before this header by consumers.
  - Korean encoding validation helpers in `kiconv_ko.h`, including UHC first-byte and second-byte validity macros.
- Related generated-style reverse mapping data exists in `kiconv_utf8_uhc.h`, with `KICONV_UTF8_UHC_MAX (17047)` and a `static kiconv_table_t kiconv_utf8_uhc[]`.
- `usr/src/uts/common/sys/Makefile` exports both `kiconv_uhc_utf8.h` and `kiconv_utf8_uhc.h`.
- File-level licensing in this chunk includes the illumos CDDL header, Sun copyright, and Unicode data permission notice.

## Risks And Invariants

- Data integrity is the main risk. A single wrong key, byte literal, deletion, or insertion can silently corrupt Korean UHC conversion.
- `KICONV_UHC_UTF8_MAX` must match the complete table row count across all chunks. The complete local file has 17,047 rows from `0x0000` through `0xFDFE`, matching the macro, but this chunk contributes only the first 8,373 rows.
- Key ordering must remain strictly ascending for lookup consumers that depend on sorted tables.
- The table mixes UHC extension Hangul, KS X 1001-style symbol mappings, and common Hangul mappings. Reviewers should avoid treating the file as a contiguous algorithmic Hangul-only range.
- Invalid byte-sequence handling is not implemented in this header; it depends on external Korean encoding validators and conversion routines.
- The `static` table-in-header pattern can increase text/data footprint if included by multiple translation units, but it also keeps the mapping private to each consumer.
- The chunk is syntactically incomplete by design: it opens the header and array but does not close the initializer, `_KERNEL`, `extern "C"`, or include guard.

## Cross-Chunk References

- Later chunks must continue from line 8454 with key `0xB297` and preserve the sorted table sequence.
- Later chunks own the remaining rows through final key `0xFDFE`, the terminating `};`, and the closing preprocessor guards.
- Per-file merge should reconcile all chunk row counts against `KICONV_UHC_UTF8_MAX (17047)` and the companion reverse table size in `kiconv_utf8_uhc.h`.
- No final per-file report was created for this chunk.

### Chunk 2: lines 8454-16909

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_uhc_utf8.h lines 8454-16909

## Scope

This chunk is part of subset A (`Docs/research_subset_a.md`) under `sources/os/illumos/illumos-gate`. I read the requested range completely: lines 8454-16909 of `usr/src/uts/common/sys/kiconv_uhc_utf8.h`. Adjacent context was used only to identify the surrounding declaration, the shared table type, the UHC byte validity macros, and the table closure.

The file is a generated/static Korean code-conversion table. This chunk contains only initializer rows inside `static kiconv_table_array_t kiconv_uhc_utf8[]`; it has no functions or local control-flow statements.

## APIs And Exported Data

The surrounding header defines, under `_KERNEL`, the UHC-to-UTF-8 table:

- `KICONV_UHC_UTF8_MAX` is defined earlier in the file as `17047`.
- `kiconv_uhc_utf8[]` is a `static kiconv_table_array_t` declared before this chunk. `kiconv_table_array_t` comes from `kiconv_cck_common.h` and has `uint32_t key` plus `uchar_t u8[4]`.
- Each visible row maps one two-byte UHC code, stored as a 16-bit-looking integer key such as `0xB297`, to a three-byte UTF-8 sequence stored as `{ 0x.., 0x.., 0x.. }`.

This chunk contributes 8456 initializer rows. The first visible row is `0xB297 -> { 0xEC, 0xBF, 0x81 }`; the last visible row is `0xFBE0 -> { 0xE9, 0x8E, 0xAC }`.

## Control Flow

There is no executable control flow in the chunk. Runtime behavior is data-driven: a caller validates UHC input bytes, combines two bytes into the table key, and looks up the key in `kiconv_uhc_utf8[]`. The sorted key order matters because common CCK code declares `kiconv_binsearch(uint32_t key, void *tbl, size_t nitems)`.

The chunk itself does not branch, allocate, lock, mutate state, or perform conversion.

## State And Invariants

All state here is immutable compile-time table data.

- 8456 rows matched the expected initializer shape.
- No malformed rows were visible.
- The key sequence is strictly increasing.
- Each row uses a UHC key and exactly three UTF-8 bytes.
- UHC trail-byte gaps such as `0x5B-0x60` and `0x7B-0x80` are structural, matching `kiconv_ko.h` validity rules.

Lead-byte coverage: partial `0xB2`, full `0xB3-0xC5`, partial `0xC6`, EUC-style `0xC7-0xC8` and `0xCA-0xFA`, and partial `0xFB`.

## Dependencies

Direct dependencies visible from context:

- `_KERNEL` guards the table definition.
- `kiconv_table_array_t` is defined in `sys/kiconv_cck_common.h`.
- UHC byte validity and Korean UDA constants are in `sys/kiconv_ko.h`.
- The reverse mapping table is `sys/kiconv_utf8_uhc.h`.
- `usr/src/uts/common/sys/Makefile` lists both UHC conversion headers.

## Risks

Manual row edits are high risk: one wrong key or UTF-8 byte silently corrupts Korean conversion. The table must remain sorted for binary-search users. `KICONV_UHC_UTF8_MAX` must match the complete table length, not this chunk length. Apparent numeric holes should not be filled automatically because they reflect invalid UHC byte ranges or separately handled ranges.

## Cross-Chunk References

Previous chunk contains the declaration and rows through `0xB296 -> { 0xEC, 0xBF, 0x80 }`; this chunk starts at `0xB297`. Next chunk continues at `0xFBE1 -> { 0xE9, 0xA0, 0x80 }` and closes the array and guards. Whole-file validation requires merging all chunks before checking the full `KICONV_UHC_UTF8_MAX == 17047` table length and sortedness.

### Chunk 3: lines 16910-17136

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_uhc_utf8.h lines 16910-17136

## Scope

- Repository subset: `Docs/research_subset_a.md`; `sources/os/illumos/illumos-gate` is in scope.
- Source span read completely: lines 16910-17136 of `usr/src/uts/common/sys/kiconv_uhc_utf8.h`.
- This is chunk 3 of an oversized header. It covers the final entries of the kernel UHC-to-UTF-8 mapping table and the file's closing conditional guards.

## APIs and Data Structures

- This chunk does not add public functions, macros, typedefs, or callable APIs.
- The table declaration is before this chunk: `static kiconv_table_array_t kiconv_uhc_utf8[]`.
- The maximum mapping macro is also before this chunk: `KICONV_UHC_UTF8_MAX` is `17047`.
- `kiconv_table_array_t` comes from `kiconv_cck_common.h` and contains a `uint32_t key` plus `uchar_t u8[4]`.
- This chunk contributes 218 mapping rows, from key `0xFBE1` at line 16910 through key `0xFDFE` at line 17127.

## Control Flow

- There is no executable control flow in this span. Runtime conversion behavior is driven by code elsewhere that includes this header and searches or indexes the static table.
- The chunk closes the `kiconv_uhc_utf8[]` initializer at line 17128.
- It then closes `_KERNEL`, the C++ `extern "C"` wrapper, and the include guard `_SYS_KICONV_UHC_UTF8_H`.

## State and Dependencies

- State is compile-time static initializer data. Under `_KERNEL`, every translation unit including this header can receive a private `static` copy of the table.
- Dependencies are the earlier table declaration, `kiconv_table_array_t`, kernel typedefs such as `uint32_t` and `uchar_t`, and external kiconv conversion routines that consume the table.
- The table is licensed through file-level CDDL and Unicode data notices outside this chunk.

## Risks and Cross-Chunk References

- Correctness risk is data integrity: wrong byte literals, missing entries, duplicate keys, or unsorted keys can silently corrupt UHC-to-UTF-8 conversion.
- The full table row count was verified as 17,047 entries, matching `KICONV_UHC_UTF8_MAX`; changes in any chunk must keep that macro synchronized.
- Prior chunks contain the header preamble, macro, table declaration, and earlier `kiconv_uhc_utf8[]` rows. This chunk owns the terminal rows and syntactic closure.
- No final per-file report was created for this chunk.
