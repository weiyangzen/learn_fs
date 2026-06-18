# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_euctw_utf8.h

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-8428, source bytes 262138, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_euctw_utf8_3b4d5de28abd_research.md`
- chunk 2: lines 8429-16875, source bytes 262144, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_euctw_utf8_c6bb328c2f7c_research.md`
- chunk 3: lines 16876-24891, source bytes 262133, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_euctw_utf8_2c25fbf3229d_research.md`
- chunk 4: lines 24892-32217, source bytes 262115, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_euctw_utf8_e97990443b4c_research.md`
- chunk 5: lines 32218-39351, source bytes 262121, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_euctw_utf8_165812130db1_research.md`
- chunk 6: lines 39352-46468, source bytes 262140, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_euctw_utf8_5aebd3c059aa_research.md`
- chunk 7: lines 46469-53594, source bytes 262139, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_euctw_utf8_fb0586632c97_research.md`
- chunk 8: lines 53595-55578, source bytes 72867, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_euctw_utf8_bbbbcb7fad1d_research.md`

## Chunk Research

### Chunk 1: lines 1-8428

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_euctw_utf8.h lines 1-8428

## Scope And Role

This chunk is the first 8,428 lines of the oversized kernel header `kiconv_euctw_utf8.h`. It contains the license/header guard, kernel-only macro declarations for CNS 11643 plane table sizes, the complete CNS plane #1 to UTF-8 mapping table, and the first 2,464 entries of the CNS plane #2 to UTF-8 mapping table. The file documents that the mapping source is Unicode 3.2 / `Unihan-3.2.0.txt`.

The chunk is data, not executable logic. It provides file-scope `static kiconv_table_array_t` arrays for EUC-TW/CNS-to-UTF-8 conversion code that can include this header in a kernel build.

## Visible APIs And Data

- Header guard: `_SYS_KICONV_EUCTW_UTF8_H`.
- Kernel gate: all conversion declarations in this chunk are inside `#ifdef _KERNEL`.
- Plane size macros visible at lines 78-85 include `KICONV_CNS1_UTF8_MAX = 5868` and `KICONV_CNS2_UTF8_MAX = 7651`, plus plane #3, #4, #5, #6, #7, and #15 sizes.
- `static kiconv_table_array_t kiconv_cns1_utf8[]` starts at line 92 and is complete in this chunk.
- `static kiconv_table_array_t kiconv_cns2_utf8[]` starts at line 5964 and continues beyond this chunk.

Each table row maps a CNS/EUC-TW two-byte key to a UTF-8 byte array. Both visible arrays begin with key `0x0000` mapped to UTF-8 replacement character bytes `{ 0xEF, 0xBF, 0xBD }`.

## Control Flow

There are no functions, branches, loops, or conversion routines in this chunk. Runtime behavior is indirect: conversion code is expected to select a plane table, search or index by `key`, and emit the populated UTF-8 bytes from `u8`.

The visible tables are `static` definitions in a header, so any translation unit including it under `_KERNEL` receives private table storage.

## State And Dependencies

The arrays are mutable static data, though they appear intended as generated immutable mapping tables. They depend on `kiconv_table_array_t` from `kiconv_cck_common.h`, which stores a `uint32_t key` and `uchar_t u8[4]`.

Related visible integration points include EUC-TW validation macros in `kiconv_tc.h`, `euctw` code-name registration in `kiconv.c`, and installation/export listing in `usr/src/uts/common/sys/Makefile`. A repository search found no direct C include/reference to `kiconv_cns1_utf8` or `kiconv_cns2_utf8` outside this header.

## Risks And Cross-Chunk References

- Plane #1 has 5,868 rows, matching `KICONV_CNS1_UTF8_MAX`; plane #2 cannot be fully validated until later chunks.
- `kiconv_cns2_utf8[]` continues after line 8428 through its close at line 13616.
- Rows with two-byte UTF-8 sequences rely on zero-initialized trailing bytes in `uchar_t u8[4]`.
- The arrays are not `const`, increasing writable kernel data footprint and accidental mutation risk.
- Later chunks contain the rest of plane #2, planes #3/#4/#5/#6/#7/#15, and closing preprocessor guards.
- Whole-file merge should verify every `KICONV_CNS*_UTF8_MAX` macro against completed array counts.

### Chunk 2: lines 8429-16875

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_euctw_utf8.h lines 8429-16875

## Scope

This report covers only lines 8429-16875 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_euctw_utf8.h` for `learn_fs` subset A. The file is a kernel iconv data header for EUC-TW/CNS 11643 to UTF-8 conversion, not filesystem or block-storage executable logic. This chunk starts mid-initializer inside the CNS 11643 plane #2 table, closes that table, opens the CNS 11643 plane #3 table, and ends mid-initializer at plane #3 key `0xC3DB`.

The whole file has 55,578 lines and declares eight CNS-to-UTF-8 tables. This chunk does not include the file license, include guard, `_KERNEL` guard, maximum-count macro definitions, later plane #3 rows, later plane #4/#5/#6/#7/#15 tables, or final preprocessor closure.

## Public Surface And APIs

No callable API is defined in this line range. The chunk contributes static kernel data to two file-scope symbols declared elsewhere in the same header:

- `kiconv_cns2_utf8[]`: this chunk contains the tail of this `static kiconv_table_array_t` table and its closing brace.
- `kiconv_cns3_utf8[]`: this chunk contains the table comment, declaration, sentinel row, and first 3,255 real mappings.

The table element type is defined in `uts/common/sys/kiconv_cck_common.h` as `uint32_t key` plus `uchar_t u8[4]`, large enough for three-byte BMP mappings and four-byte supplementary-plane mappings.

## Data Layout Visible In This Chunk

This line range contains 8,443 initializer rows total:

- Plane #2 tail: 5,187 rows, from `0xBBB4` at line 8429 through `0xF2C4` at line 13615.
- Plane #3 start: 3,256 rows, from the sentinel `0x0000 -> EF BF BD` at line 13620 through `0xC3DB` at line 16875.

The plane #2 rows in this chunk are all three-byte UTF-8 mappings. The visible plane #3 rows include 3,206 three-byte mappings and 50 four-byte mappings, beginning at `0xA1C4` and last seen at `0xC3B3`.

A numeric scan over the chunk found no duplicate keys and no nonascending keys within the visible plane #2 tail or visible plane #3 segment.

## Control Flow

There is no executable control flow in this chunk. Runtime behavior is table-driven by conversion code outside this header:

1. EUC-TW byte validation is described in `kiconv_tc.h`.
2. The converter identifies the CNS plane and forms a two-byte CNS key.
3. The selected `kiconv_cnsN_utf8[]` array is searched as sorted `kiconv_table_array_t` data.
4. The matched `u8[]` byte sequence is copied to the UTF-8 output buffer.
5. Generic kiconv code handles buffer accounting, invalid-sequence policy, replacement behavior, and errno values.

The conversion-name registry in `uts/common/os/kiconv.c` maps `"euctw"` to internal code id `16`.

## State And Dependencies

All state visible in this chunk is immutable static initializer data compiled into kernel code that includes this header under `_KERNEL`. There are no locks, allocations, I/O operations, mutable globals, reference counts, or filesystem state transitions.

Direct dependencies include `kiconv_table_array_t` from `kiconv_cck_common.h`, EUC-TW validation macros from `kiconv_tc.h`, and the companion reverse-direction table `kiconv_utf8_euctw.h`.

## Risks And Invariants

Important invariants:

- Full-table row counts must match `KICONV_CNS2_UTF8_MAX` and `KICONV_CNS3_UTF8_MAX` across all chunks.
- Keys must remain sorted within each plane table for binary search.
- CNS plane selection must match the table selected here.
- UTF-8 byte sequences must be copied using their actual encoded length, not by blindly emitting all four storage bytes.

Risks visible in this chunk:

- Generated-data drift can silently corrupt EUC-TW conversion for affected characters.
- This report starts mid-plane #2 and ends mid-plane #3, so whole-array count validation requires adjacent chunks.
- Four-byte UTF-8 handling is required for visible plane #3 rows.
- Plane #3 includes the `0x0000` replacement row in this chunk; plane #2's sentinel is in an earlier chunk.

## Cross-Chunk References

Prior chunk(s) must supply the header guard, `_KERNEL` guard, max-count macros, all of `kiconv_cns1_utf8[]`, and the start of `kiconv_cns2_utf8[]` through `0xBBB3`.

Later chunk(s) must continue `kiconv_cns3_utf8[]` from `0xC3DC` at line 16876 through its close, then cover CNS planes #4, #5, #6, #7, and #15 plus final preprocessor closure.

### Chunk 3: lines 16876-24891

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_euctw_utf8.h lines 16876-24891

## Scope

This chunk is a contiguous slice of the illumos kernel EUC-TW-to-UTF-8 mapping header. It begins inside `kiconv_cns3_utf8[]`, ends inside `kiconv_cns4_utf8[]`, and contains no executable functions or local control-flow branches. Its behavior is entirely data-driven: kernel iconv code indexes or searches static `kiconv_table_array_t` entries to translate CNS 11643/EUC-TW code points into UTF-8 byte sequences.

## APIs And Data Structures

- Provides part of `static kiconv_table_array_t kiconv_cns3_utf8[]` from lines 16876-20015, covering 3,139 entries from key `0xC3DC` through `0xE7AA`.
- Provides the start and middle of `static kiconv_table_array_t kiconv_cns4_utf8[]` from lines 20018-24891, covering 4,873 entries from the sentinel `0x0000` through key `0xD4F8`.
- The entry type comes from `kiconv_cck_common.h`: `uint32_t key; uchar_t u8[4];`. The `u8[4]` payload supports both 3-byte BMP UTF-8 and 4-byte supplementary-plane UTF-8.
- The maximum-count constants declared near the file top remain the table-level contract for this chunk: `KICONV_CNS3_UTF8_MAX` is `6395`, and `KICONV_CNS4_UTF8_MAX` is `7287`.

## Control Flow And State

There is no direct control flow in this line range. Runtime behavior depends on the conversion layer selecting the correct CNS plane table, locating an entry by `key`, using `u8_number_of_bytes[first_byte]` to determine output length, checking output capacity, and copying the stored UTF-8 bytes.

The chunk is stateless read-only kernel data. It allocates no memory, mutates no globals, and performs no locking. Any conversion state, error handling, replacement-character policy, and buffer advancement live in the kiconv conversion wrappers and plane-selection code outside this chunk.

## Data Shape

- `kiconv_cns3_utf8[]` portion: 3,139 entries, key range `0xC3DC` to `0xE7AA`, with 3,118 three-byte entries and 21 four-byte entries.
- `kiconv_cns4_utf8[]` portion: 4,873 entries, key range `0x0000` sentinel then `0xA1A1` to `0xD4F8`, with 2,619 three-byte entries and 2,254 four-byte entries.
- Ordering checks over both portions found no descending or duplicate key transitions.
- `kiconv_cns4_utf8[]` starts with `0x0000 -> EF BF BD`, matching the replacement-character sentinel pattern used by other tables in this header.

## Dependencies

- `_KERNEL` guard: the arrays are only exposed for kernel builds.
- `kiconv_table_array_t` from `sys/kiconv_cck_common.h`.
- UTF-8 byte-length validation/copying depends on `u8_number_of_bytes[]`, declared in common kiconv headers and provided by Unicode textprep code.
- EUC-TW plane parsing is related to macros in `sys/kiconv_tc.h`, including `KICONV_TC_EUCTW_MBYTE`, `KICONV_TC_EUCTW_PMASK`, and valid EUC-TW byte checks.
- Reverse-direction mapping lives in `sys/kiconv_utf8_euctw.h`; this chunk is for CNS/EUC-TW to UTF-8 direction only.
- `usr/src/uts/common/sys/Makefile` lists `kiconv_euctw_utf8.h` as an exported kernel header.

## Risks And Cross-Chunk References

- Count drift risk: if entries are added or removed, `KICONV_CNS3_UTF8_MAX` and `KICONV_CNS4_UTF8_MAX` must stay aligned with the full arrays.
- Sort-order risk: binary-search users require monotonically increasing keys within each table; edits must preserve ordering across chunk boundaries.
- Boundary risk: this chunk crosses the plane #3/#4 array boundary at lines 20015-20018.
- Previous chunk should cover the beginning of `kiconv_cns3_utf8[]` up to key `0xC3DB`; this chunk continues at `0xC3DC`.
- Next chunk must continue `kiconv_cns4_utf8[]` at line 24892, key `0xD4F9`, after this chunk ends at key `0xD4F8`.

### Chunk 4: lines 24892-32217

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_euctw_utf8.h lines 24892-32217

## Scope

This chunk is part of illumos `kiconv_euctw_utf8.h`, a kernel-only static conversion-table header for EUC-TW/CNS 11643 to UTF-8 conversion. The source tree `sources/os/illumos/illumos-gate` is in `Docs/research_subset_a.md`.

The line range contains no executable functions. It covers:

- The tail of `kiconv_cns4_utf8[]`, from CNS plane 4 key `0xD4F9` through the end of the table at `0xEEDC`.
- The start and middle of `kiconv_cns5_utf8[]`, including the replacement/sentinel row `0x0000 -> EF BF BD`, then CNS plane 5 keys from `0xA1A1` through `0xD5B4`.
- One table boundary: `kiconv_cns4_utf8[]` closes at line 27306, and `kiconv_cns5_utf8[]` starts at line 27309.

Within this exact range there are 7,322 mapping rows: 2,414 rows from plane 4 and 4,908 rows from plane 5. Of those rows, 5,837 encode four-byte UTF-8 sequences beginning with `0xF0`, and 1,485 encode shorter UTF-8 sequences stored in the same four-byte array field.

## APIs and Data Exposed

- `kiconv_cns4_utf8[]` and `kiconv_cns5_utf8[]` are `static kiconv_table_array_t` arrays, so they have translation-unit-local linkage in whichever kernel source includes this header.
- `kiconv_table_array_t` is defined in `kiconv_cck_common.h` as `{ uint32_t key; uchar_t u8[4]; }`.
- Each row maps a 16-bit CNS code key, written as a `uint32_t`, to up to four UTF-8 bytes.
- The plane 5 table starts with `0x0000, { 0xEF, 0xBF, 0xBD }`, matching the file's convention for a replacement-character row.
- The file-level maximums visible outside this chunk declare `KICONV_CNS4_UTF8_MAX` as 7,287 and `KICONV_CNS5_UTF8_MAX` as 8,602; the full arrays match those counts.

There are no callable APIs, macros, structs, or typedefs introduced inside this chunk.

## Control Flow

There is no control flow in the chunk itself. Conversion control flow is data-driven in consumers: a EUC-TW/CNS input key is expected to select the appropriate plane table, then locate the matching `key` row and copy the nonzero UTF-8 bytes from `u8`.

The only structural transition is the source-level array boundary:

1. Continue plane 4 mappings inherited from previous chunks.
2. Close `kiconv_cns4_utf8[]`.
3. Open `kiconv_cns5_utf8[]`.
4. Continue plane 5 mappings into the next chunk.

## State

The chunk contributes immutable static table data. It has no mutable state, locks, counters, allocation, initialization function, or teardown path.

Important state properties for consumers:

- Row order is ascending within each plane segment in this chunk.
- Plane 4 and plane 5 are separate lookup domains; the duplicate-looking CNS key space across arrays is intentional because the CNS plane number is external to the row key.
- UTF-8 byte arrays are fixed-width at four bytes. Three-byte mappings are represented by only three explicit initializer bytes; C zero-initialization fills the remaining byte.
- The sentinel/replacement row exists at the start of plane 5, not at the plane 4 continuation point in this chunk.

## Dependencies

This chunk depends on file-level context outside the range:

- `_SYS_KICONV_EUCTW_UTF8_H` include guard and `_KERNEL` guard wrap the whole table header.
- `kiconv_table_array_t` and `uchar_t` come from common kernel/iconv headers, especially `kiconv_cck_common.h`.
- The full header is listed for installation/build handling in `usr/src/uts/common/sys/Makefile`.
- Reverse-direction EUC-TW conversion data lives separately in `kiconv_utf8_euctw.h`.

No OS/VFS/block-storage APIs are used directly here despite the subset scope; this is kernel character-conversion data.

## Risks and Edge Cases

- Table count coupling: consumers or generated lookup metadata must keep `KICONV_CNS4_UTF8_MAX` and `KICONV_CNS5_UTF8_MAX` synchronized with the complete array lengths. This chunk includes the plane 4 close and plane 5 open, making off-by-one mistakes at the boundary easy to introduce if regenerated manually.
- Plane-key ambiguity: the same 16-bit key values can appear in different CNS plane arrays. Consumers must include plane selection in lookup state and cannot treat keys as globally unique.
- Variable UTF-8 length in fixed storage: rows with three explicit bytes rely on zero-filled trailing bytes. Consumers must know how output length is determined and avoid copying all four bytes blindly for shorter mappings.
- Sparse CNS ranges: keys are monotonically increasing in this chunk but are not a dense arithmetic range; index arithmetic based only on key deltas would be unsafe without a table/search layer.
- Generated-data review risk: thousands of hex rows provide little local semantic signal. Corruption in an individual mapping would compile cleanly and likely surface only as conversion mismatch.
- Header inclusion cost: because the arrays are `static` in a header, every including translation unit gets private copies unless the build intentionally includes it in only one converter implementation.

## Cross-Chunk References

- Earlier chunks define the top of the file, include guards, `KICONV_CNS*_UTF8_MAX` constants, and complete plane 1 through plane 3 tables.
- The immediately preceding chunk starts `kiconv_cns4_utf8[]` at line 20018 and supplies its first 4,873 rows through key `0xD4F8`.
- This chunk completes `kiconv_cns4_utf8[]` with 2,414 additional rows, ending at key `0xEEDC`.
- This chunk starts `kiconv_cns5_utf8[]` at line 27309 and covers its first 4,908 rows through key `0xD5B4`.
- The next chunk must continue `kiconv_cns5_utf8[]` from the row after `0xD5B4`, finish plane 5, and then cover later plane tables depending on its assigned range.
- Later chunks contain `kiconv_cns6_utf8[]`, `kiconv_cns7_utf8[]`, `kiconv_cns15_utf8[]`, and the closing `_KERNEL`/include-guard directives.

### Chunk 5: lines 32218-39351

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_euctw_utf8.h lines 32218-39351

## Scope

This chunk is inside the illumos kernel-only EUC-TW/CNS11643 to UTF-8 conversion header. The requested range is entirely static mapping data plus one table boundary:

- Lines 32218-35911: tail of `static kiconv_table_array_t kiconv_cns5_utf8[]`.
- Lines 35912-35913: close of plane 5 table.
- Lines 35914-35916: start of `static kiconv_table_array_t kiconv_cns6_utf8[]`, including its `0x0000` replacement-character sentinel.
- Lines 35917-39351: early/middle portion of plane 6 mappings.

## APIs And Data Types

No callable API, macro, or executable function is defined in this chunk. The data belongs to the kernel character conversion subsystem.

Entries use `kiconv_table_array_t`:

```c
typedef struct {
	uint32_t key;
	uchar_t u8[4];
} kiconv_table_array_t;
```

Each mapping stores a CNS11643/EUC-TW two-byte key and UTF-8 output bytes. Three-byte UTF-8 entries rely on C zero-initialization for the unused fourth byte; four-byte mappings fill all bytes.

## Table Coverage

Mechanical scan found 7,130 initializers including the plane-6 sentinel, or 7,129 real CNS keys:

- `kiconv_cns5_utf8`: 3,694 entries, `0xD5B5` through `0xFCD1`.
- `kiconv_cns6_utf8`: 3,436 entries including sentinel, `0x0000` through `0xC5D5`.
- Plane 6 real entries here: 3,435 entries, `0xA1A1` through `0xC5D5`.

UTF-8 byte lengths:

- 6,830 four-byte mappings.
- 300 three-byte mappings.

Real CNS keys are monotonically increasing within each table segment. Apart from the intentional `0x0000` sentinel, keys use valid EUC/CNS byte ranges.

## Control Flow And State

There is no local control flow. External EUC-TW parsing identifies the CNS plane and key, then looks up the selected `kiconv_cnsN_utf8` table.

The chunk contributes immutable static kernel storage. It has no mutable state, locks, allocations, or runtime initialization.

## Dependencies

- `_KERNEL` controls compilation of these tables.
- `kiconv_table_array_t` defines the storage layout.
- `KICONV_CNS5_UTF8_MAX` and `KICONV_CNS6_UTF8_MAX` must match full table sizes and sentinel conventions.
- `kiconv_tc.h` provides EUC-TW validation and plane parsing macros.
- `kiconv.c` registers encoding name `euctw` with code id `16`.

## Risks

- Sentinel handling matters: `kiconv_cns6_utf8` starts with `0x0000 -> EF BF BD`.
- Consumers must not blindly emit all four `u8` bytes for three-byte UTF-8 mappings.
- Because arrays are `static` in a header, each includer can receive a private copy unless build structure avoids that.
- Data errors are behavioral bugs: one wrong key, byte, comma, or ordering change can silently corrupt conversion.
- Mappings are documented as Unicode 3.2/Unihan 3.2.0, so updating to newer Unicode data requires reverse-table compatibility review.

## Cross-Chunk References

- Previous chunks contain the file header, max-count macros, planes 1-4, and the beginning of plane 5 through `0xD5B4`.
- This chunk completes plane 5 and starts plane 6.
- Later chunks continue plane 6 after `0xC5D5`, then define planes 7 and 15.
- Reverse conversion data lives in `kiconv_utf8_euctw.h`; round-trip behavior depends on consistency between the two headers.

### Chunk 6: lines 39352-46468

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_euctw_utf8.h lines 39352-46468

## Scope

This report covers lines 39352-46468 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_euctw_utf8.h` for `learn_fs` subset A. The file is generated-style kernel iconv data for EUC-TW/CNS 11643 to UTF-8 conversion. This chunk starts inside the CNS 11643 plane #6 table, closes that table, opens the CNS 11643 plane #7 table, and ends inside plane #7 at key `0xCDBC`.

The slice is table data only. It does not include the file header, include guard, `_KERNEL` guard start, the `KICONV_CNS*_UTF8_MAX` definitions, the start of `kiconv_cns6_utf8`, the end of `kiconv_cns7_utf8`, or the later `kiconv_cns15_utf8` table.

## Public Surface And APIs

The chunk contributes rows to two kernel-only static arrays declared elsewhere in the same header:

- `static kiconv_table_array_t kiconv_cns6_utf8[]` for CNS 11643 plane #6 to UTF-8.
- `static kiconv_table_array_t kiconv_cns7_utf8[]` for CNS 11643 plane #7 to UTF-8.

The relevant maximum constants are outside this chunk but visible in the same file:

- `KICONV_CNS6_UTF8_MAX (6386)`.
- `KICONV_CNS7_UTF8_MAX (6538)`.

The element type is defined in `uts/common/sys/kiconv_cck_common.h`:

- `uint32_t key`
- `uchar_t u8[4]`

Each row maps a CNS/EUC-TW two-byte code value to a UTF-8 byte sequence. Most visible rows use four explicit UTF-8 bytes for supplementary-plane Unicode code points; some use three explicit bytes and rely on zero-initialization for the remaining byte in `u8[4]`.

## Data Layout Visible In This Chunk

This line range contains 7,113 mapping rows total:

- 2,950 rows from the tail of `kiconv_cns6_utf8`, starting at line 39352 with key `0xC5D6` and ending at line 42301 with key `0xE4FA`.
- The closing `};` for `kiconv_cns6_utf8` at line 42302.
- The comment and declaration for `kiconv_cns7_utf8` at lines 42304-42305.
- 4,163 rows from the start of `kiconv_cns7_utf8`, starting at line 42306 with sentinel key `0x0000 -> EF BF BD` and ending at line 46468 with key `0xCDBC`.

Initializer widths in this chunk:

- 6,921 rows with four explicit UTF-8 bytes.
- 192 rows with three explicit UTF-8 bytes.

Within each visible table segment, keys are strictly ascending and no duplicate keys were found. `kiconv_cns6_utf8` as a whole contains 6,386 rows, matching `KICONV_CNS6_UTF8_MAX`; `kiconv_cns7_utf8` as a whole contains 6,538 rows, matching `KICONV_CNS7_UTF8_MAX`.

## Control Flow

There is no executable control flow in this chunk. Runtime behavior is supplied by the kernel iconv conversion code that consumes these static tables:

1. EUC-TW input validation is handled by macros in `kiconv_tc.h`, including `KICONV_TC_EUCTW_MBYTE`, `KICONV_TC_EUCTW_PMASK`, and `KICONV_TC_IS_VALID_EUCTW_SEQ`.
2. The converter identifies the CNS plane and forms the two-byte table key.
3. Generic CCK conversion support can search sorted `kiconv_table_array_t` tables via `kiconv_binsearch()`.
4. On a match, the `u8[4]` bytes are copied to UTF-8 output according to the converter's output-length logic.
5. On invalid input or absent mapping, error/replacement policy is handled by the surrounding kiconv implementation, not by this data table.

The conversion name registry in `uts/common/os/kiconv.c` assigns `"euctw"` code id `16`, tying these CNS tables to the kernel EUC-TW conversion surface.

## State And Dependencies

All state in this chunk is immutable static initializer data compiled into translation units that include the header under `_KERNEL`.

Direct dependencies and adjacent contracts:

- `_KERNEL` gating around the complete table definitions.
- `kiconv_table_array_t` from `kiconv_cck_common.h`.
- `uchar_t` and `uint32_t` from illumos system type headers included before this generated data header.
- EUC-TW byte and plane validation macros in `kiconv_tc.h`.
- Reverse-direction companion data in `kiconv_utf8_euctw.h`.
- Header export listing in `uts/common/sys/Makefile`.

The file-level comment states that the mapping supports Unicode 3.2 and uses `Unihan-3.2.0.txt` as its mapping source. This chunk inherits that version/source constraint.

## Risks And Invariants

Key invariants:

- Table keys must remain sorted for binary-search consumers.
- Per-plane row counts must match `KICONV_CNS6_UTF8_MAX` and `KICONV_CNS7_UTF8_MAX`.
- UTF-8 byte sequences must remain valid and correctly zero-padded in `u8[4]`.
- The sentinel row `0x0000 -> U+FFFD` at the start of `kiconv_cns7_utf8` must remain first in that table.

Risks visible in this chunk:

- Generated-data drift: a single incorrect byte changes character conversion while preserving valid C syntax.
- Cross-chunk count drift: the chunk begins after the start of plane #6 and ends before the end of plane #7, so full-table validation requires adjacent chunks.
- Include-time footprint: arrays are `static` in a header, so each including translation unit gets private table storage.
- Zero-fill dependence: three-byte initializers depend on C zero-initialization for the unused fourth byte.
- Sparse key ranges are intentional; missing CNS code points are not represented by placeholder rows except for each table's `0x0000` replacement sentinel.
- Direct textual consumers of `kiconv_cns6_utf8` and `kiconv_cns7_utf8` were not found outside this header in `usr/src`, suggesting inclusion or generation patterns may be indirect.

## Cross-Chunk References

The preceding chunk must cover the start of `kiconv_cns6_utf8` from line 35915 through key `0xC5D5` at line 39351. Together with this chunk, plane #6 should total 6,386 rows and close at line 42302.

The following chunk must continue `kiconv_cns7_utf8` at line 46469 with key `0xCDBD`, run through the table close at line 48844, and then account for the `kiconv_cns15_utf8` declaration beginning at line 48847. Plane #7 should total 6,538 rows, leaving 2,375 plane #7 rows after this chunk.

### Chunk 7: lines 46469-53594

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_euctw_utf8.h lines 46469-53594

## Scope

This chunk is part of illumos `kiconv_euctw_utf8.h`, a kernel-only static conversion-table header for EUC-TW/CNS 11643 to UTF-8 conversion. The source tree `sources/os/illumos/illumos-gate` is in `Docs/research_subset_a.md`.

The line range contains no executable functions. It covers:

- The tail of `kiconv_cns7_utf8[]`, from CNS plane 7 key `0xCDBD` through the end of the table at `0xE6D5`.
- The start and middle of `kiconv_cns15_utf8[]`, including the replacement/sentinel row `0x0000 -> EF BF BD`, then CNS plane 15 keys from `0xA1A1` through `0xD6E5`.
- One table boundary: `kiconv_cns7_utf8[]` closes at line 48844, and `kiconv_cns15_utf8[]` starts at line 48847.

Within this exact range there are 7,122 mapping rows: 2,375 rows from plane 7 and 4,747 rows from plane 15. Of those rows, 6,874 encode four-byte UTF-8 sequences beginning with `0xF0`, and 248 encode three-byte UTF-8 sequences stored in the same fixed four-byte array field.

## APIs and Data Exposed

- `kiconv_cns7_utf8[]` and `kiconv_cns15_utf8[]` are `static kiconv_table_array_t` arrays, so they have translation-unit-local linkage in whichever kernel source includes this header.
- `kiconv_table_array_t` is defined in `kiconv_cck_common.h` as `{ uint32_t key; uchar_t u8[4]; }`.
- Each row maps a CNS row/cell-style key, written as a `uint32_t`, to up to four UTF-8 bytes.
- The plane 15 table starts with `0x0000, { 0xEF, 0xBF, 0xBD }`, matching the file's replacement-character convention.
- The file-level maximums outside this chunk declare `KICONV_CNS7_UTF8_MAX` as 6,538 and `KICONV_CNS15_UTF8_MAX` as 6,722; full-array counts match those constants.

There are no callable APIs, macros, structs, typedefs, or include directives introduced inside this chunk.

## Control Flow

There is no control flow in the chunk itself. Runtime conversion is data-driven: EUC-TW parsing identifies the CNS plane and key, the converter selects the corresponding `kiconv_cns*_utf8[]` table, then lookup code emits the mapped UTF-8 byte sequence.

The only structural transition is the source-level array boundary:

1. Continue plane 7 mappings inherited from the previous chunk.
2. Close `kiconv_cns7_utf8[]`.
3. Open `kiconv_cns15_utf8[]`.
4. Continue plane 15 mappings into the next chunk.

## State

The chunk contributes immutable static table data. It has no mutable state, locking, reference counts, allocation, initialization function, or teardown path.

Important state properties for consumers:

- Row order is ascending within each plane segment in this chunk. The only key decrease is intentional at the plane boundary, where plane 7 ends at `0xE6D5` and plane 15 restarts with `0x0000`.
- Plane 7 and plane 15 are separate lookup domains. Many key values repeat across the two arrays, but the CNS plane number is external state and makes those mappings distinct.
- UTF-8 byte arrays are fixed-width at four bytes. Three-byte mappings rely on C zero-initialization for the unused trailing byte.
- The sentinel/replacement row appears at the start of plane 15, not at the plane 7 continuation point.

## Dependencies

This chunk depends on file-level and neighboring kiconv context outside the range:

- `_SYS_KICONV_EUCTW_UTF8_H` include guard and `_KERNEL` guard wrap the full table header.
- `kiconv_table_array_t` and `uchar_t` come from common kernel/iconv headers, especially `kiconv_cck_common.h`.
- EUC-TW byte/plane parsing helpers are declared in `kiconv_tc.h`, including the `0x8E` multibyte introducer and CNS plane mask constants.
- The broader kiconv framework advertises `euctw` as a supported code name in `uts/common/os/kiconv.c`.
- The full header is listed in `usr/src/uts/common/sys/Makefile`.
- Reverse-direction UTF-8 to EUC-TW conversion data lives separately in `kiconv_utf8_euctw.h`.

No OS/VFS/block-storage APIs are used directly here despite the subset scope; this is kernel character-conversion data.

## Risks and Edge Cases

- Table count coupling: `KICONV_CNS7_UTF8_MAX` and `KICONV_CNS15_UTF8_MAX` must stay synchronized with the complete generated arrays. This chunk includes a close/open boundary where manual regeneration errors can create off-by-one defects.
- Plane-key ambiguity: repeated key values across plane 7 and plane 15 are expected. Any consumer that ignores plane selection and treats the key as globally unique will return incorrect characters.
- Variable UTF-8 length in fixed storage: rows with three explicit bytes rely on zero-filled trailing bytes. Consumers must determine output length correctly and avoid blindly copying all four bytes for every row.
- Sparse CNS ranges: keys are monotonically increasing inside each plane segment but not dense. Lookup code must search table entries rather than derive an array offset directly from the key.
- Generated-data integrity: an individual hex mapping can be corrupted without a compile-time failure; verification needs data-level comparison against the intended Unicode/CNS source tables.
- Header inclusion cost: because these arrays are `static` in a header, every including translation unit gets private copies unless the build intentionally includes it in only one converter implementation.

## Cross-Chunk References

- Earlier chunks define the file header, include guards, `KICONV_CNS*_UTF8_MAX` constants, and complete plane 1 through plane 6 tables.
- The immediately preceding chunk starts `kiconv_cns7_utf8[]` at line 42305 and covers its first 4,163 rows through key `0xCDBC`.
- This chunk completes `kiconv_cns7_utf8[]` with 2,375 additional rows, ending at key `0xE6D5`.
- This chunk starts `kiconv_cns15_utf8[]` at line 48847 and covers its first 4,747 rows through key `0xD6E5`.
- The next chunk must continue `kiconv_cns15_utf8[]` from key `0xD6E6`, finish plane 15 through key `0xEDB9`, and then cover the closing `_KERNEL`, C++ linkage, and include-guard directives near the end of the file.

### Chunk 8: lines 53595-55578

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_euctw_utf8.h lines 53595-55578

## Scope

This report covers lines 53595-55578 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_euctw_utf8.h` for `learn_fs` subset A. The chunk is generated/static conversion data, not executable filesystem logic. It is the tail of the file: the final segment of the CNS 11643 plane #15 to UTF-8 table, followed by the closing initializer, `_KERNEL` guard, C++ linkage guard, and header include guard.

Adjacent context shows that this chunk belongs to:

- `static kiconv_table_array_t kiconv_cns15_utf8[]`, declared at line 48847.
- `KICONV_CNS15_UTF8_MAX (6722)`, the declared maximum mapping count for plane #15.
- `kiconv_table_array_t`, defined in `kiconv_cck_common.h` as `{ uint32_t key; uchar_t u8[4]; }`.

## Public Surface And APIs

This chunk does not define functions, macros, or callable APIs. Its public surface is the continuation and closure of the file-local static table `kiconv_cns15_utf8[]`, compiled only under `_KERNEL`.

The visible table entries map CNS 11643 plane #15 two-byte row/cell keys to UTF-8 byte arrays. The chunk contributes 1,975 mappings from key `0xD6E6` through `0xEDB9`. Values are stored directly as 3-byte or 4-byte UTF-8 sequences in a fixed four-byte array; shorter 3-byte values rely on normal zero-initialization of the remaining byte in the aggregate.

Across the complete plane #15 table, adjacent context confirms 6,722 entries, matching `KICONV_CNS15_UTF8_MAX`.

## Control Flow

There is no executable control flow in this chunk. Runtime control flow is external to this header: kernel iconv EUC-TW conversion code selects the table for the active CNS plane, searches by `key`, and copies the `u8` bytes to the UTF-8 output buffer.

## State And Dependencies

State is immutable static kernel data. There are no locks, counters, heap allocations, device references, VFS objects, or filesystem state transitions.

Dependencies include `_KERNEL`, `kiconv_table_array_t` from `kiconv_cck_common.h`, illumos kernel/common C types such as `uchar_t` and `uint32_t`, and Unicode 3.2 / `Unihan-3.2.0.txt` mapping data noted near the file top.

## Risks And Cross-Chunk References

Primary risks are entry-count drift from `KICONV_CNS15_UTF8_MAX`, sorted-key breakage for lookup code, accidental loss of sparse gaps, and misreading `u8[4]` as four meaningful bytes for every entry.

Earlier chunks define the shared header, constants, and plane #1, #2, #3, #4, #5, #6, #7, plus the beginning and middle of plane #15. This chunk is the final merge segment for `kiconv_cns15_utf8[]` and closes the whole header.
