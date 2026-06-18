# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_hkscs_utf8.h

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-8168, source bytes 262130, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_hkscs_utf8_c32285a21fa2_research.md`
- chunk 2: lines 8169-16638, source bytes 262120, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_hkscs_utf8_dde57a153ec0_research.md`
- chunk 3: lines 16639-18497, source bytes 59170, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_hkscs_utf8_946c43bae506_research.md`

## Chunk Research

### Chunk 1: lines 1-8168

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_hkscs_utf8.h lines 1-8168

## Scope

This chunk covers the first 8,168 lines of `kiconv_hkscs_utf8.h`. It includes the license/header guard, `_KERNEL` gate, `KICONV_HKSCS_UTF8_MAX`, and the prefix of the static BIG5-HKSCS(2004)-to-UTF-8 mapping table. The chunk ends mid-table at key `0xbce1`; later chunks contain the rest of the initializer and closing preprocessor blocks.

## APIs And Data Contracts

- Header guard: `_SYS_KICONV_HKSCS_UTF8_H`.
- Kernel-only declaration: table content is inside `#ifdef _KERNEL`.
- Macro: `KICONV_HKSCS_UTF8_MAX` is `18403`.
- Data object: `static kiconv_table_array_t kiconv_hkscs_utf8[]`.
- Element contract from `kiconv_cck_common.h`: `uint32_t key` plus `uchar_t u8[4]`.

The table is sorted by encoded HKSCS key and stores 2-, 3-, or 4-byte UTF-8 payloads.

## Chunk Contents

- Lines 1-66: CDDL, Sun, and Unicode notices.
- Lines 68-81: guard/opening declarations and table start.
- Lines 82-8168: 8,083 mapping rows.

Structured findings:

- First row: `0x0000 -> { 0xEF, 0xBF, 0xBD }`.
- Last row in chunk: `0xbce1 -> { 0xE6, 0xBE, 0x84 }`.
- No duplicate keys found in this chunk.
- Keys are strictly ascending.
- Row byte lengths: 107 two-byte rows, 6,574 three-byte rows, 1,402 four-byte rows.
- Special sentinel rows: `0x8862`, `0x8864`, `0x88a3`, `0x88a5` map to `0xFF` placeholder sequences, with adjacent comments showing decomposed UTF-8 alternatives.

## Control Flow

No runtime control flow is defined here. Runtime behavior is data-driven: consumers include the header, binary-search or otherwise index the sorted table, infer output size from the first UTF-8 byte, and copy `u8[]` bytes to the output buffer.

## State And Dependencies

The table is effectively immutable conversion data, though not declared `const`. It depends on kernel kiconv types and UTF-8 helper tables from the common kiconv stack, especially `kiconv_table_array_t`, `uchar_t`, and `u8_number_of_bytes`.

Related files visible in the same subsystem include reverse and compatibility tables: `kiconv_utf8_hkscs.h`, `kiconv_cp950hkscs_utf8.h`, and `kiconv_utf8_cp950hkscs.h`.

## Risks And Cross-Chunk Notes

- Full table count must later be reconciled against `KICONV_HKSCS_UTF8_MAX`.
- Binary-search consumers require the complete table to remain sorted.
- `0xFF` sentinel rows need special consumer handling; they are not ordinary UTF-8.
- Because the array is `static` in a header, multiple includes can duplicate a large table.
- This chunk is syntactically incomplete by itself; the next chunk should continue at `0xbce2` and preserve key ordering.

### Chunk 2: lines 8169-16638

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_hkscs_utf8.h lines 8169-16638

## Scope

- Repository subset: `Docs/research_subset_a.md`; `sources/os/illumos/illumos-gate` is in scope.
- Source span read completely: lines 8169-16638 of `usr/src/uts/common/sys/kiconv_hkscs_utf8.h`.
- This is chunk 2 of an oversized generated-style conversion header. It is wholly inside the `static kiconv_table_array_t kiconv_hkscs_utf8[]` initializer and does not include the declaration or closing brace.

## APIs and Data Structures

- No callable API, macro, typedef, or function body is defined in this chunk.
- The chunk contributes rows to `kiconv_hkscs_utf8[]`, the HKSCS-2004 to UTF-8 mapping table declared earlier in the file under `_KERNEL`.
- Adjacent context shows the associated constant `KICONV_HKSCS_UTF8_MAX` is declared before the table with value `18403`.
- `kiconv_table_array_t` is defined in `kiconv_cck_common.h` as:
  - `uint32_t key`
  - `uchar_t u8[4]`
- Each entry in this chunk maps a packed two-byte BIG5-HKSCS code value to a UTF-8 byte sequence stored inline in `u8`.

## Mapping Coverage

- The chunk contains 8,470 table rows.
- First row: `0xbce2 -> { 0xE6, 0xBD, 0x91 }`.
- Last row: `0xf34b -> { 0xE8, 0xB6, 0xAC }`.
- It starts immediately after prior-chunk key `0xbce1` and ends immediately before next-chunk key `0xf34c`.
- Keys are strictly increasing within the chunk and all visible trail bytes are in valid BIG5 trail-byte ranges (`0x40-0x7e` or `0xa1-0xfe`).
- UTF-8 byte widths in this chunk:
  - 8,389 rows use three bytes.
  - 78 rows use two bytes.
  - 3 rows use four bytes: `0xc87a`, `0xc87c`, and `0xc8a4`.
- No duplicate keys or duplicate UTF-8 byte sequences were found within this chunk.

## Control Flow

- There is no local executable control flow. Runtime behavior depends on converter code that includes this static table and searches it.
- The strict key ordering is a functional contract for binary-search style lookup code. `kiconv_cck_common.h` declares `kiconv_binsearch(uint32_t key, void *tbl, size_t nitems)`.
- The table rows do not carry explicit UTF-8 lengths. Consumers must infer or otherwise know how many bytes in `uchar_t u8[4]` are payload for each result.

## State and Dependencies

- State is compile-time static mapping data. Because the array is declared `static` in a header, every translation unit that includes the header can receive its own private copy.
- Dependencies include `_KERNEL` guarding, `kiconv_table_array_t`, `uint32_t`, `uchar_t`, and BIG5/HKSCS byte validity rules from nearby kiconv headers such as `kiconv_tc.h`.
- `usr/src/uts/common/sys/Makefile` lists `kiconv_hkscs_utf8.h` among exported/common sys headers.

## Risks and Edge Cases

- Data integrity is the main risk: a wrong byte literal or missing row silently changes conversion behavior for one HKSCS character.
- The mix of two-, three-, and four-byte UTF-8 payloads means lookup consumers must not assume uniform sequence length.
- The `uchar_t u8[4]` field has no separate length member; shorter sequences rely on consistent consumer handling.
- Gaps are normal for invalid or unmapped BIG5 byte slots. Consumers must rely on lookup failure handling rather than assuming contiguous keys.
- `KICONV_HKSCS_UTF8_MAX` is outside this chunk; full-table row-count validation must reconcile all chunks, including sentinel or non-mapping rows.

## Cross-Chunk References

- Chunk 1 owns the file preamble, guards, `KICONV_HKSCS_UTF8_MAX`, the table declaration, the `0x0000` replacement entry, and mappings up through `0xbce1`.
- This chunk continues the same array from `0xbce2` through `0xf34b` without opening or closing syntax.
- Chunk 3 resumes at `0xf34c`, finishes the table at `0xfefe`, and closes the array and file guards.
- The final per-file report should merge this with adjacent chunk reports; it was not created here.

### Chunk 3: lines 16639-18497

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_hkscs_utf8.h lines 16639-18497

## Scope

- Repository subset: `Docs/research_subset_a.md` (`sources/os/illumos/illumos-gate` is in scope).
- Source span read completely: lines 16639-18497 of `usr/src/uts/common/sys/kiconv_hkscs_utf8.h`.
- This is chunk 3 of an oversized header. It covers the tail of the `kiconv_hkscs_utf8[]` static HKSCS-2004 to UTF-8 mapping table and the file's closing conditional guards.

## APIs and Data Structures

- The file declares `KICONV_HKSCS_UTF8_MAX` and `static kiconv_table_array_t kiconv_hkscs_utf8[]` near the top of the header, before this chunk.
- `kiconv_table_array_t` is defined in `kiconv_cck_common.h` as `uint32_t key` plus `uchar_t u8[4]`.
- Each row in this chunk is a table initializer mapping one BIG5-HKSCS code value to a UTF-8 byte sequence stored in `u8`.
- This chunk contributes 1,850 mapping rows, from key `0xf34c` at line 16639 through key `0xfefe` at line 18488.
- UTF-8 values include both three-byte BMP encodings and four-byte supplementary-plane encodings. In this chunk, 288 rows visibly contain a leading `0xF0` byte.

## Control Flow

- There is no executable control flow in this span. It is static data for conversion routines elsewhere.
- The chunk closes the table at line 18489, closes `_KERNEL` at line 18491, closes the C++ guard at lines 18493-18495, and closes `_SYS_KICONV_HKSCS_UTF8_H` at line 18497.

## State and Dependencies

- State is compile-time, read-only table content once linked into kernel consumers that include this header.
- Dependencies are `kiconv_table_array_t` from `usr/src/uts/common/sys/kiconv_cck_common.h`, kernel typedefs such as `uint32_t` and `uchar_t`, and the enclosing `_KERNEL` guard.
- `usr/src/uts/common/sys/Makefile` lists `kiconv_hkscs_utf8.h`, so the header is part of the exported/common sys header set.

## Mapping Coverage

- Starts mid-`0xf3xx`: `0xf34c -> { 0xE8, 0xB6, 0xAA }`.
- Continues across `0xf4xx` through `0xfexx`, with expected BIG5/HKSCS gaps where low-byte values are invalid or unmapped.
- Ends at `0xfefe -> { 0xE7, 0xA7, 0x94 }`.
- Visible internal gaps near the tail include `0xfdf1`, `0xfe52`, `0xfe6f`, `0xfeaa`, and `0xfedd`.

## Risks and Cross-Chunk Notes

- Correctness risk is data integrity: a wrong byte literal or missing row silently corrupts conversion for that character.
- The fixed `uchar_t u8[4]` field requires consumers to handle three-byte and four-byte UTF-8 lengths correctly.
- Because the table is `static` in a header, each kernel translation unit that includes it may get a private copy.
- `KICONV_HKSCS_UTF8_MAX` is declared before this chunk as `18403`; row-count changes anywhere in the full table must stay synchronized.
- Prior chunks own the header preamble, constants, and earlier table rows. This chunk starts after `0xf34b` and owns the syntactic end of the table and file guards.
- No final per-file report was created.
