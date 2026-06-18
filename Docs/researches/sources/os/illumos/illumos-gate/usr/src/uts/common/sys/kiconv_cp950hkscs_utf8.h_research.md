# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_cp950hkscs_utf8.h

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-8439, source bytes 262128, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_cp950hkscs_6ff328ae6497_research.md`
- chunk 2: lines 8440-16910, source bytes 262133, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_cp950hkscs_165d8ee02570_research.md`
- chunk 3: lines 16911-18412, source bytes 46380, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_cp950hkscs_310019403723_research.md`

## Chunk Research

### Chunk 1: lines 1-8439

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_cp950hkscs_utf8.h lines 1-8439

## Scope

This report covers lines 1-8439 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_cp950hkscs_utf8.h` for `learn_fs` subset A. The file is a kernel-only generated/static conversion table, not executable filesystem logic. This chunk starts at the CDDL/Unicode license block and header guard, defines the table metadata, opens the `kiconv_cp950hkscs_utf8[]` initializer, and continues through CP950HKSCS key `0xbf4c`. The closing initializer and header guard are outside this chunk; the whole source file has 18,412 lines.

## Public Surface And APIs

This chunk contributes two kernel-visible symbols when `_KERNEL` is defined:

- `KICONV_CP950HKSCS_UTF8_MAX` is defined as `18322`, the advertised maximum mapping count for CP950HKSCS-to-UTF-8 conversion.
- `static kiconv_table_array_t kiconv_cp950hkscs_utf8[]` starts the mapping table from CP950HKSCS code units to UTF-8 byte arrays.

The include guard is `_SYS_KICONV_CP950HKSCS_UTF8_H`, with `extern "C"` wrapping for C++ consumers. Because the table is declared `static` in a header, each translation unit that includes it gets its own internal-linkage copy. The table element type comes from `kiconv_cck_common.h`: `kiconv_table_array_t` contains a `uint32_t key` and `uchar_t u8[4]` for CCK-encoding-to-UTF-8 mappings.

## Data Layout Visible In This Chunk

The initializer begins with a sentinel/default-style mapping:

- `0x0000 -> { 0xEF, 0xBF, 0xBD }`, which is UTF-8 for U+FFFD replacement character.

After that, keys are CP950HKSCS double-byte values in ascending numeric order. This chunk contains 8,358 initializer rows total: the `0x0000` row plus 8,357 high-byte rows from `0x8840` through `0xbf4c`. A numeric scan found no non-monotonic keys in this line range, which is important because the shared kiconv layer exposes binary-search table lookup.

Visible key coverage by leading byte is:

- `0x88`: 73 rows, `0x8840`-`0x88aa`.
- `0x89` through `0xa2`: mostly dense Big5-style lead-byte ranges using valid trail bytes `0x40`-`0x7e` and `0xa1`-`0xfe`, with gaps where CP950HKSCS has no mapping.
- `0xa3`: 95 rows, ending at `0xa3e1`.
- `0xa4` through `0xbe`: full 157-row lead-byte ranges, `xx40`-`xxfe` over valid Big5 trail-byte slots.
- `0xbf`: starts in this chunk with 13 rows, `0xbf40`-`0xbf4c`; continuation begins in the next chunk.

UTF-8 output byte lengths visible here are either 2-byte or 3-byte sequences. A scan counted 102 two-byte outputs and 8,256 three-byte outputs in this chunk. The table stores outputs in a four-byte fixed field, so shorter sequences rely on zero-initialization of the unused trailing bytes in C aggregate initialization.

## Control Flow

There is no executable control flow in this chunk. Runtime behavior is table-driven:

1. Higher-level kiconv code recognizes the normalized code name `cp950hkscs` as code id `17` in `uts/common/os/kiconv.c`.
2. Traditional Chinese conversion logic validates Big5-family byte sequences using macros such as `KICONV_TC_IS_BIG5_1st_BYTE()` and `KICONV_TC_IS_BIG5_2nd_BYTE()` from `kiconv_tc.h`.
3. The CP950HKSCS double-byte value is used as a lookup key in a `kiconv_table_array_t` table.
4. Shared CCK helpers, including `kiconv_binsearch()`, are the visible dependency for sorted-table lookup.
5. The matched `u8[]` bytes are emitted to the UTF-8 output buffer by conversion code outside this header.

Because this chunk only defines data, all buffer accounting, invalid-sequence handling, replacement behavior, and errno decisions are delegated to the including conversion implementation and common kiconv helpers.

## State And Dependencies

State is immutable static table data after compilation. There are no locks, counters, mutable globals, allocation paths, I/O paths, or filesystem-facing state transitions in this chunk.

Direct dependencies visible or implied by this chunk are:

- `_KERNEL`: the table is only exposed for kernel builds.
- `kiconv_table_array_t`, `uchar_t`, and integer typedefs from the common kiconv/sys type headers.
- `kiconv_cck_common.h` for the CCK table shape and binary-search helper contract.
- `kiconv_tc.h` for Big5-family byte validity rules used by Traditional Chinese conversion code.
- `uts/common/os/kiconv.c` for public code-name registration; `cp950hkscs` maps to internal code id `17`.
- Companion reverse mapping header `kiconv_utf8_cp950hkscs.h` for UTF-8-to-CP950HKSCS conversion, outside this chunk.

## Risks And Invariants

The key invariants are table completeness, strict ascending key order, output byte correctness, and agreement between `KICONV_CP950HKSCS_UTF8_MAX` and the complete table size across all chunks. This chunk alone cannot verify the final count because it ends mid-initializer.

Important risks:

- Generated-data drift: a single wrong byte sequence silently corrupts filename/text conversion for affected CP950HKSCS characters.
- Binary-search fragility: any out-of-order row would make lookup unreliable; this chunk is sorted, but later chunks must preserve that invariant.
- Fixed-width UTF-8 storage: two-byte entries depend on implicit zero fill in `u8[4]`; consumers must stop output at the intended UTF-8 length rather than blindly copying four bytes.
- Header-level `static` data can duplicate a large table in every including object if included broadly.
- This file maps many characters into Unicode private-use-looking ranges such as `EF 8C..EF 95` early in the table; compatibility with external CP950HKSCS expectations depends on the exact Unicode data version and Sun modifications noted in the header comments.
- The chunk is unrelated to filesystem/block semantics except as kernel text conversion infrastructure that can affect path/name encoding when used by filesystems or kernel consumers.

## Cross-Chunk References

The next chunk must continue the open `kiconv_cp950hkscs_utf8[]` initializer at key `0xbf4d`, confirm that key ordering remains ascending, and eventually verify the closing brace, `_KERNEL`/C++ guard closure, and total mapping count against `KICONV_CP950HKSCS_UTF8_MAX`. Later chunks also need to identify the final key range and whether any four-byte UTF-8 outputs appear after line 8439.

### Chunk 2: lines 8440-16910

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_cp950hkscs_utf8.h lines 8440-16910

## Scope

This report covers lines 8440-16910 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_cp950hkscs_utf8.h` for `learn_fs` subset A. The file is an illumos kernel iconv data header for CP950-HKSCS-to-UTF-8 conversion. This chunk is an interior slice of the static mapping table: it starts at CP950-HKSCS key `0xbf4d` and ends at key `0xf576`, without including the file header, macro definition, table declaration, closing initializer, or preprocessor guard closes.

The reviewed range contains 8,471 complete mapping rows. The whole file contains 18,322 rows, matching `KICONV_CP950HKSCS_UTF8_MAX`, so this chunk accounts for only the middle portion of the file-level table.

## Public Surface And APIs

This chunk introduces no new public functions, macros, typedefs, or declarations. It contributes initializer rows to the kernel-only table declared earlier in the file:

- `#define KICONV_CP950HKSCS_UTF8_MAX (18322)`
- `static kiconv_table_array_t kiconv_cp950hkscs_utf8[] = { ... }`

The table element type is defined in `usr/src/uts/common/sys/kiconv_cck_common.h` as:

- `uint32_t key`
- `uchar_t u8[4]`

Rows in this chunk use a two-byte CP950-HKSCS code value as `key` and a UTF-8 byte sequence as `u8`. Most rows have three explicit UTF-8 bytes; 78 rows have two explicit bytes and rely on C zero-initialization for the remaining `u8[4]` bytes.

## Data Layout Visible In This Chunk

The chunk is sorted table data. It begins immediately after line 8439's `0xbf4c` entry:

- line 8440: `0xbf4d -> { 0xE7, 0x87, 0x90 }`

It ends immediately before line 16911's `0xf577` entry:

- line 16910: `0xf576 -> { 0xE9, 0xB0, 0x89 }`

Measured properties for lines 8440-16910:

- Mapping rows counted: 8,471.
- First key: `0xbf4d`.
- Last key: `0xf576`.
- Duplicate keys in this chunk: none.
- Nonascending keys in this chunk: none.
- Explicit UTF-8 byte widths: 8,393 rows with three bytes, 78 rows with two bytes.
- Trail-byte validation: all keys use CP950/Big5-style trail bytes in `0x40-0x7e` or `0xa1-0xfe`; no rows use invalid trail bytes `0x7f-0xa0`.

The visible lead-byte coverage is `0xbf` through `0xf5`. Full lead-byte groups generally contain 157 rows, matching the valid Big5 trail-byte count after excluding `0x7f-0xa0`. Partial groups occur at the chunk boundaries: `0xbf` starts at trail `0x4d`, and `0xf5` ends at trail `0x76`.

The mapped Unicode/UTF-8 payloads are mainly CJK ideographs and related symbols. The range also includes two-byte UTF-8 mappings for non-CJK characters such as combining marks and Cyrillic letters around the `0xc6d8` and `0xc7f3` regions. Consumers must therefore use the leading UTF-8 byte or stored payload length logic rather than assuming every row emits exactly three bytes.

## Control Flow

There is no executable control flow in this chunk. Runtime behavior is data-driven and belongs to the kernel iconv conversion code that uses these CCK tables:

1. Caller-side conversion logic validates and combines a CP950-HKSCS byte pair into a table key.
2. The sorted `kiconv_table_array_t` table can be searched, typically through the shared `kiconv_binsearch()` helper declared in `kiconv_cck_common.h`.
3. On a match, the `u8` bytes are copied to the output buffer. Generic iconv code in `uts/common/os/kiconv.c` uses `u8_number_of_bytes[first_byte]` for table-driven UTF-8 output in analogous CCK-to-UTF-8 paths.
4. Missing or invalid input mappings are handled by caller policy, including error or replacement behavior; this header only supplies static mapping data.

The `cp950hkscs` name is registered in `uts/common/os/kiconv.c` with code ID `17`, linking this table family to the kernel iconv charset registry.

## State And Dependencies

All state in this chunk is immutable static initializer data compiled under the file's `_KERNEL` guard. There is no allocation, locking, reference counting, I/O, filesystem state, or mutable global state in the reviewed lines.

Direct dependencies and adjacent integration points:

- `kiconv_table_array_t` from `usr/src/uts/common/sys/kiconv_cck_common.h`.
- Kernel/system integer and byte types such as `uint32_t` and `uchar_t`.
- `usr/src/uts/common/sys/Makefile`, which lists `kiconv_cp950hkscs_utf8.h` for installation/export alongside related kiconv tables.
- `kiconv_utf8_cp950hkscs.h`, the companion reverse-direction UTF-8-to-CP950-HKSCS table.
- `kiconv_hkscs_utf8.h` and `kiconv_big5_utf8.h`, neighboring Traditional Chinese mapping tables with similar static-data structure.
- `uts/common/os/kiconv.c`, which registers the normalized charset name `cp950hkscs`.

A direct `.c` include or direct symbol reference to `kiconv_cp950hkscs_utf8` was not found by textual search in this checkout; build integration may be generated, indirect, or outside the searched direct-reference pattern. This report therefore treats the table as installed kernel conversion data without asserting a specific include site.

## Risks And Invariants

The critical invariants are data-table invariants:

- The full table count must remain exactly `KICONV_CP950HKSCS_UTF8_MAX` entries. This chunk contributes 8,471 of the whole file's 18,322 rows.
- Keys must remain sorted for binary-search consumers. This chunk is strictly ascending from `0xbf4d` through `0xf576`.
- Duplicate keys would make conversion ambiguous. No duplicates were found in this chunk.
- Big5/CP950 trail-byte gaps are intentional. Automated table normalization must not insert or reinterpret invalid `0x7f-0xa0` trail positions.
- Two-byte UTF-8 payload rows depend on zero-filled trailing slots in `uchar_t u8[4]`; consumers must derive output length from UTF-8 leading-byte rules or equivalent metadata.
- Generated-data drift is hard to review semantically. A syntactically valid edit can still corrupt a character mapping, so validation should prefer generated-source comparison, whole-table count/order checks, and conversion tests.
- Since the table is `static` in a header, every translation unit that includes it under `_KERNEL` receives a private copy. That may be intentional for this iconv table pattern, but broad inclusion would increase kernel text/data footprint.

## Cross-Chunk References

The previous chunk must provide the license, include guard, `_KERNEL` wrapper, `KICONV_CP950HKSCS_UTF8_MAX`, the opening `kiconv_cp950hkscs_utf8[]` declaration, the replacement row `0x0000 -> EF BF BD`, and all entries through line 8439/key `0xbf4c`.

This chunk starts cleanly at line 8440/key `0xbf4d` and ends cleanly at line 16910/key `0xf576`. The next chunk must resume at line 16911/key `0xf577`, continue through the final key `0xfefe`, and close the table initializer plus `_KERNEL`, C++ `extern "C"`, and `_SYS_KICONV_CP950HKSCS_UTF8_H` guards.

### Chunk 3: lines 16911-18412

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_cp950hkscs_utf8.h lines 16911-18412

## Scope

This report covers only ordered chunk 3 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_cp950hkscs_utf8.h`, lines 16911-18412, within learn_fs subset A (`Docs/research_subset_a.md`). I read the requested line range completely and used adjacent context only to identify the enclosing declaration, table type, header guards, and kiconv table contract. This chunk is static conversion data, not executable kernel logic.

## APIs And Exported Data

The chunk is the tail of `static kiconv_table_array_t kiconv_cp950hkscs_utf8[]`, declared earlier in the same header under `_KERNEL`. Adjacent context identifies:

- `KICONV_CP950HKSCS_UTF8_MAX` as `18322`, the advertised maximum mapping count for this CP950HKSCS-to-UTF-8 table.
- `kiconv_cp950hkscs_utf8[]` as a `static` header-defined table whose entries have a 32-bit CP950HKSCS key and a four-byte UTF-8 byte array (`uchar_t u8[4]`) from `kiconv_cck_common.h`.

Lines 16911-18403 contribute 1493 final mapping entries. The first entry in this chunk maps CP950HKSCS key `0xf577` to UTF-8 bytes `E9 B6 9F`; the final entry maps `0xfefe` to `E7 A7 94`. Lines 18404-18412 close the array, the `_KERNEL` conditional, the C++ `extern "C"` wrapper, and the `_SYS_KICONV_CP950HKSCS_UTF8_H` header guard.

No functions, macros, typedefs, enums, syscalls, ioctls, locks, callbacks, or VFS/filesystem APIs are defined in this range.

## Control Flow

There is no runtime control flow in this chunk: no branches, loops, calls, allocation, locking, or error paths. Runtime behavior is indirect through whichever CP950HKSCS-to-UTF-8 converter includes this generated header and searches `kiconv_cp950hkscs_utf8[]`.

The only control-like behavior visible here is preprocessor structure inherited from the full header:

- Table data exists only when `_KERNEL` is defined.
- The table symbol is `static`, so each including translation unit receives a private copy rather than a global external symbol.
- C++ linkage guards are closed after the kernel-only data.

Lookup-sensitive behavior is implied by the table contract in `kiconv_cck_common.h`: `kiconv_table_array_t` is intended for CCK-encoding-to-UTF-8 mappings, and common code exposes `kiconv_binsearch()`. The key column in this chunk remains sorted in ascending CP950HKSCS order, with valid-code gaps preserved rather than filled.

## State And Data Layout

The state contributed by this chunk is immutable conversion-table state embedded in kernel text/data by inclusion. Each initializer has the form:

`0x<cp950hkscs>, { <utf8 byte 1>, <utf8 byte 2>, <utf8 byte 3> }`

Although `kiconv_table_array_t.u8` has four bytes, this chunk supplies three-byte UTF-8 sequences; the fourth byte is zero-initialized by C aggregate rules. This matters for consumers that copy until a zero terminator or otherwise expect a fixed four-byte slot.

The chunk spans the high CP950HKSCS key range:

- `0xf577` through `0xf9d6`: mostly CJK ideograph mappings.
- `0xf9dd` through `0xf9fe`: box drawing/block glyphs, including UTF-8 for U+255x box-drawing characters and U+2593.
- `0xfa40` onward: a mix of CJK Extension/compatibility-looking mappings and many UTF-8 private-use mappings beginning with `EE 80 xx`, `EE 81 xx`, through `EE 8C xx`.
- `0xfe40` through `0xfefe`: final high-key mappings, again mixing assigned CJK characters and private-use code points.

Several CP950HKSCS code positions are absent in the high ranges, for example gaps around `0xfa5f`, `0xfa66`, `0xfabd`, `0xfac5`, `0xfad5`, `0xfb48`, `0xfbb8`, `0xfbf3`, `0xfbf9`, `0xfc4f`, `0xfc6c`, `0xfcb9`, `0xfce2`, `0xfcf1`, `0xfdb7`, `0xfdb8`, `0xfdbb`, `0xfdf1`, `0xfe52`, `0xfe6f`, `0xfeaa`, and `0xfedd`. These holes are part of the encoding map and must not be compacted into assumed contiguous indexes unless the lookup layer explicitly uses the sorted keys.

## Dependencies

Direct compile-time dependencies visible from adjacent context:

- `kiconv_cck_common.h` for `kiconv_table_array_t`.
- Kernel build context via `_KERNEL`.
- Header guard `_SYS_KICONV_CP950HKSCS_UTF8_H`.
- C++ compatibility wrapper.
- illumos integer/character typedefs such as `uchar_t` and `uint32_t`, through the common kiconv headers.

Related kiconv dependencies visible in nearby source:

- `kiconv.c` registers normalized code name `cp950hkscs` with code id `17`.
- `kiconv_utf8_cp950hkscs.h` is the reverse-direction UTF-8-to-CP950HKSCS table.
- `usr/src/uts/common/sys/Makefile` installs this header alongside the other kernel kiconv mapping headers.

I did not find a direct C include of this specific header under `usr/src/uts` with a simple repository grep, so this report treats consumers conservatively as generated/module/include-time users of the installed kernel mapping header rather than naming an unverified direct call site.

## Risks And Correctness Notes

- Table order is semantically important for binary-search-style consumers. Reordering or sorting by UTF-8 bytes instead of CP950HKSCS keys would break lookup.
- Missing key positions are meaningful. Filling, renumbering, or array-indexing as if this were dense CP950HKSCS space can produce wrong conversions.
- Private-use UTF-8 mappings (`EE 80 xx` and related ranges) are compatibility-sensitive. Updating them to modern Unicode scalars without coordinated reverse-table and locale behavior changes could break round-tripping.
- The three-byte initializer style relies on the fourth `u8` byte being zero-initialized. Mechanical rewrites that change the table type, packing, or copy length could alter termination behavior.
- Because the table is `static` in a header, multiple including objects can each get their own copy. That is expected for this generated header pattern, but careless inclusion in many compilation units would increase kernel object size.
- This table has licensing provenance from Unicode data plus Sun modifications in the file header; regenerated mappings need to preserve the license notices and modification notices.

## Cross-Chunk References

This chunk starts mid-table; chunks 1 and 2 contain the file header, `KICONV_CP950HKSCS_UTF8_MAX`, the `kiconv_cp950hkscs_utf8[]` declaration, and all earlier CP950HKSCS key ranges. This chunk completes that same table and closes the file. There is no later chunk for this file after line 18412.
