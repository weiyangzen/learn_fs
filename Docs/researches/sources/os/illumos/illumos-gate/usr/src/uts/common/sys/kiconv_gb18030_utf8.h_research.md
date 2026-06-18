# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb18030_utf8.h

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-8450, source bytes 262121, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_gb18030_ut_7e071de4db64_research.md`
- chunk 2: lines 8451-16906, source bytes 262136, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_gb18030_ut_b497b6ac091f_research.md`
- chunk 3: lines 16907-25455, source bytes 262130, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_gb18030_ut_253dd6ad3b22_research.md`
- chunk 4: lines 25456-33002, source bytes 262135, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_gb18030_ut_2c8f7fa57fd5_research.md`
- chunk 5: lines 33003-40491, source bytes 262115, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_gb18030_ut_fd8da32c8e57_research.md`
- chunk 6: lines 40492-47980, source bytes 262115, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_gb18030_ut_98cf8c45216f_research.md`
- chunk 7: lines 47981-55469, source bytes 262115, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_gb18030_ut_48036989b978_research.md`
- chunk 8: lines 55470-62958, source bytes 262115, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_gb18030_ut_4aeee84f92d9_research.md`
- chunk 9: lines 62959-63457, source bytes 17244, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_gb18030_ut_52f2ab032db3_research.md`

## Chunk Research

### Chunk 1: lines 1-8450

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb18030_utf8.h lines 1-8450

## Scope

This report covers lines 1-8450 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb18030_utf8.h` for `learn_fs` subset A. The file is a kernel iconv data header for GB18030/GBK to UTF-8 conversion. This chunk includes the license notices, include guard, C++ linkage wrapper, `_KERNEL` guard, both maximum-count macros, and the first 8,367 rows of the two-byte GBK/GB18030 mapping table. It ends inside `kiconv_gbk_utf8[]` at key `0xAD45`; it does not include the end of the two-byte table, the four-byte `kiconv_gbk4_utf8[]` table, or the closing preprocessor structure.

The slice is exactly 8,450 lines and 262,121 bytes. The whole file is 63,457 lines, so later chunks must account for most of the table data and all closing guards.

## Public Surface And APIs

This chunk exposes kernel-only static data and constants when `_KERNEL` is defined:

- `KICONV_GBK_UTF8_MAX (23941)`: declared maximum item count for the two-byte GBK/GB18030-to-UTF-8 table.
- `KICONV_GBK4_UTF8_MAX (39421)`: declared maximum item count for the four-byte GB18030-to-UTF-8 table, although the table itself starts later at line 24027.
- `static kiconv_table_array_t kiconv_gbk_utf8[] = { ... }`: begins the two-byte mapping table.

The table element type is defined in `kiconv_cck_common.h` as `uint32_t key` plus `uchar_t u8[4]`. This header does not declare callable functions.

## Data Layout Visible In This Chunk

`kiconv_gbk_utf8[]` starts at line 83. The first row is `0x0000 -> EF BF BD`, the UTF-8 replacement character `U+FFFD`.

Within lines 1-8450:

- Mapping rows counted: 8,367.
- First key: `0x0000`.
- Last key: `0xAD45`.
- Duplicate keys found: none.
- Nonascending keys found: none.
- Explicit UTF-8 byte initializer widths: 158 rows with two bytes, 8,209 rows with three bytes.
- Rows containing `0xEE` UTF-8 bytes: 1,109.

The visible key ranges are regular GBK-style two-byte ranges. `0x8140` through `0xACFE` are complete lead-byte blocks, and `0xAD40` through `0xAD45` are the first six rows of the next block. The chunk boundary is clean at line 8450; line 8451 continues with `0xAD46`.

## Control Flow

There is no executable control flow in this chunk. Runtime behavior is supplied by illumos kernel iconv code that consumes these CCK conversion tables:

1. GB18030/GBK input validation is handled outside this header, using Simplified Chinese byte macros from `kiconv_sc.h`.
2. A valid input sequence is assembled into a numeric key.
3. Generic lookup code such as `kiconv_binsearch()` can search sorted conversion tables.
4. On match in `kiconv_gbk_utf8[]`, the `u8` byte array supplies the UTF-8 output bytes.
5. Error handling, replacement policy, ASCII passthrough, and buffer accounting are external.

## State And Dependencies

All state in this chunk is immutable static initializer data compiled into translation units that include this header under `_KERNEL`.

Direct or required dependencies:

- `_KERNEL`
- `kiconv_table_array_t` from `uts/common/sys/kiconv_cck_common.h`
- `uchar_t` and `uint32_t`
- `kiconv_sc.h` for GBK/GB18030 byte validation and length macros
- `kiconv_utf8_gb18030.h` as the companion reverse-direction table
- `uts/common/sys/Makefile`, which exports this and related kiconv headers

The conversion registry in `uts/common/os/kiconv.c` includes `"gb18030"`, plus `"gbk"`, `"cp936"`, and `"936"` aliases for the Simplified Chinese conversion surface.

## Risks And Invariants

Important invariants:

- `kiconv_gbk_utf8[]` must remain sorted by ascending `key` for binary search.
- Full table length must remain exactly `KICONV_GBK_UTF8_MAX`.
- The later four-byte table must remain exactly `KICONV_GBK4_UTF8_MAX`.
- UTF-8 byte arrays must contain valid output sequences and compatible zero padding.

Risks:

- Generated-data drift can silently change conversion semantics.
- This chunk validates only 8,367 of 23,941 two-byte rows.
- The table is `static` in a header, so broad inclusion can duplicate data.
- 158 rows depend on zero-filled trailing bytes in `u8[4]`.
- Private-use mappings using `0xEE...` bytes may be mistaken for invalid data by naive validators.

## Cross-Chunk References

The next chunk should resume at line 8451 with `0xAD46`. Later chunks must verify:

- Remaining two-byte rows through `0xFEFE` at line 24024.
- `kiconv_gbk4_utf8[]` starts at line 24027.
- Four-byte table closes at line 63449.
- Final guards close `_KERNEL`, C++ linkage, and `_SYS_KICONV_GB18030_UTF8_H`.
- Whole-file row counts remain `gbk_entries=23941` and `gbk4_entries=39421`.

### Chunk 2: lines 8451-16906

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb18030_utf8.h lines 8451-16906

## Scope

This report covers lines 8451-16906 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb18030_utf8.h` for `learn_fs` subset A. The entire chunk is inside the kernel-only `static kiconv_table_array_t kiconv_gbk_utf8[]` initializer, continuing the two-byte GBK/GB18030-to-UTF-8 mapping table that began in chunk 1. It contains mapping data only: no functions, macros, conditionals, or table boundaries are introduced in this slice.

## Public And Internal APIs Covered

- No callable API is defined in this chunk.
- The chunk contributes 8,456 rows to `kiconv_gbk_utf8[]`, the static table for GB18030 two-byte character input mapped to UTF-8 byte arrays.
- The table element type is `kiconv_table_array_t` from `kiconv_cck_common.h`:
  - `uint32_t key`: packed source character code.
  - `uchar_t u8[4]`: UTF-8 output bytes, with this chunk using three explicit bytes per row and the fourth slot zero-initialized by C.
- The relevant full-table count contract, declared earlier in the file, is `KICONV_GBK_UTF8_MAX (23941)`.

## Data Covered

- First row in this chunk: line 8451, `0xAD46 -> E7 92 85`.
- Last row in this chunk: line 16906, `0xD9A6 -> E4 BD B4`.
- The rows are sorted by ascending GBK/GB18030 key across the chunk.
- Syntax check of the requested range found 8,456 initializer rows, all matching the same `0xKEY, { 0xNN, 0xNN, 0xNN },` shape.
- UTF-8 payload shape check found all rows using valid three-byte UTF-8 byte ranges: lead byte `0xE4` through `0xE9` or private-use lead `0xEE`, followed by continuation bytes.
- The chunk includes both ordinary Unicode mappings and GBK/GB18030 compatibility/private-use mappings. The private-use style entries use `0xEE ...` UTF-8 sequences and appear within the two-byte table.
- A visible transition occurs near the end of the chunk: line 16900 still maps sequential keys into `E8 B4 xx`, while line 16901 begins key `0xD9A1` mapping back to lower Unicode ranges such as `E4 BD 9F`. This is table data, not control flow.

## Control Flow And Behavior

There is no local control flow in this chunk. Runtime behavior is supplied by the kiconv implementation that includes or otherwise compiles this static header table:

1. GB18030/GBK input validation classifies a character as a two-byte sequence using the byte-range macros in `kiconv_sc.h`.
2. The packed two-byte source code is looked up in `kiconv_gbk_utf8[]`.
3. On match, the `u8` array bytes from the table element become the UTF-8 output.
4. On miss or invalid byte sequence, behavior is determined by the caller's kiconv error/replacement policy outside this header.

The sorted ordering visible in this chunk is therefore a behavioral invariant: any binary-search-based lookup depends on the table remaining ordered by `key`.

## State And Data Structures

- The only state represented here is immutable static conversion data.
- No per-conversion state, locks, reference counts, allocations, or mutable globals are present in the chunk.
- Each row is independent, but the table as a whole has global invariants:
  - rows must remain sorted by `key`;
  - row count must stay consistent with `KICONV_GBK_UTF8_MAX`;
  - payload bytes must remain valid UTF-8 byte sequences for the output copy path;
  - the table must remain inside the surrounding `_KERNEL` guard established earlier in the file.

## Dependencies

- `kiconv_table_array_t` and `uchar_t` are provided by the broader illumos kernel/kiconv header environment, specifically `kiconv_cck_common.h` for the table shape.
- `kiconv_sc.h` defines GBK/GB18030 byte validation macros that determine whether runtime input can reach this two-byte table.
- `uts/common/sys/Makefile` lists `kiconv_gb18030_utf8.h` with the exported kiconv headers.
- Companion reverse-direction data lives in `kiconv_utf8_gb18030.h`; this chunk is only for GB18030/GBK to UTF-8.
- `uts/common/os/kiconv.c` registers `"gb18030"` and related Simplified Chinese encoding names in the kernel iconv surface, but direct textual references to `kiconv_gbk_utf8` outside this header were not found in the searched tree, so use may be indirect through kiconv build/include structure.

## Risks And Invariants

- Ordering risk: a misplaced row would break binary search or produce missed mappings.
- Count drift risk: edits in this chunk must preserve the full `KICONV_GBK_UTF8_MAX` table length, even though the macro is declared outside the chunk.
- Boundary risk: this chunk begins and ends mid-table. The previous chunk must end at `0xAD45`; the next chunk must continue at `0xD9A7`.
- Encoding risk: the `u8[4]` field is fixed-width, while rows here initialize only three bytes. Callers must infer/copy the correct UTF-8 length from byte classification or zero termination, not assume all four slots are meaningful payload.
- Data-generation risk: many rows are mechanical mapping constants. Manual edits are easy to get wrong and should be verified against GB18030/GBK source tables and by structural checks over the whole header.
- Private-use compatibility risk: rows using `0xEE ...` are not ordinary CJK scalar mappings; removing or normalizing them could break round-trip behavior expected by legacy GBK/GB18030 consumers.

## Cross-Chunk References

- Chunk 1 (`lines 1-8450`) defines the file guard, C++ wrapper, `_KERNEL` guard, `KICONV_GBK_UTF8_MAX`, `KICONV_GBK4_UTF8_MAX`, and starts `kiconv_gbk_utf8[]`; it ends at key `0xAD45`.
- This chunk continues `kiconv_gbk_utf8[]` from `0xAD46` through `0xD9A6`.
- Chunk 3 (`lines 16907-25455`) continues at key `0xD9A7`, finishes `kiconv_gbk_utf8[]` at `0xFEFE`, closes that table, and starts `kiconv_gbk4_utf8[]`.
- Later chunks cover the four-byte GB18030 table and the closing `_KERNEL`, C++ wrapper, and header guard structure.

### Chunk 3: lines 16907-25455

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb18030_utf8.h lines 16907-25455

## Scope

This chunk is a contiguous slice of an illumos kernel GB18030/GBK-to-UTF-8 mapping header. It begins inside the two-byte `kiconv_gbk_utf8[]` table, closes that table at lines 24024-24025, and then starts the four-byte `kiconv_gbk4_utf8[]` table at line 24027. It contains no executable functions; runtime behavior is entirely data-driven by common kiconv lookup and copy code outside this header.

## APIs And Data Structures

- Provides the tail of `static kiconv_table_array_t kiconv_gbk_utf8[]` from line 16907 through line 24024, covering 7,118 two-byte GBK/GB18030 keys from `0xD9A7` through `0xFEFE`.
- Defines the beginning of `static kiconv_table_array_t kiconv_gbk4_utf8[]` from line 24027 through line 25455, covering 1,428 four-byte GB18030 keys from the sentinel `0x00000000` through `0x81319136`.
- The entry type is `kiconv_table_array_t` from `sys/kiconv_cck_common.h`: `uint32_t key; uchar_t u8[4];`. This chunk stores 2-byte and 3-byte UTF-8 sequences in the fixed four-byte `u8` field.
- The table-size constants declared near the top of this same file are the full-table contracts: `KICONV_GBK_UTF8_MAX` is `23941`, and `KICONV_GBK4_UTF8_MAX` is `39421`.

## Control Flow And State

There is no local control flow, allocation, locking, or mutable state in this line range. The arrays are `static` kernel-only read-mostly data under the surrounding `_KERNEL` guard.

At runtime, common kiconv code receives a mapping-table ID or converter-specific table pointer, computes or searches for a `key`, derives the UTF-8 output length from `u8_number_of_bytes[entry.u8[0]]`, checks output capacity, and copies the stored bytes. Invalid-input handling, `EILSEQ`/`E2BIG`, replacement-character policy, buffer advancement, and conversion descriptor state are all implemented outside this chunk.

## Data Shape

- Total entries in this chunk: 8,546.
- `kiconv_gbk_utf8[]` portion: 7,118 entries, all two-byte keys, all with 3-byte UTF-8 payloads.
- `kiconv_gbk4_utf8[]` portion: 1,428 entries. The first is the `0x00000000 -> EF BF BD` replacement-character sentinel; the remaining entries begin at `0x81308130` and continue through `0x81319136`.
- UTF-8 payload widths in this chunk: 7,119 three-byte entries and 1,427 two-byte entries. The 3-byte count includes the four-byte-table sentinel.
- Mechanical checks over each table segment found no duplicate keys and no descending key transitions.

## Dependencies

- `_KERNEL` guard in this header limits these arrays to kernel builds.
- `kiconv_table_array_t` and the `u8_number_of_bytes[]` declaration come from `sys/kiconv_cck_common.h`.
- `usr/src/uts/common/os/kiconv.c` contains the common conversion loops that use `u8_number_of_bytes` and table entries to validate length, handle output capacity, and copy UTF-8 bytes.
- `usr/src/uts/common/sys/Makefile` exports `kiconv_gb18030_utf8.h` with the other kernel iconv headers.
- Reverse-direction UTF-8-to-GB18030 mappings live in `sys/kiconv_utf8_gb18030.h`; this chunk covers only GB18030/GBK to UTF-8 data.

## Risks And Cross-Chunk References

- Count drift risk: edits to either table must keep `KICONV_GBK_UTF8_MAX` and `KICONV_GBK4_UTF8_MAX` aligned with the full arrays, not just this chunk.
- Ordering risk: lookup code can rely on sorted mapping tables; generated or manual changes must preserve monotonic order across chunk boundaries.
- Boundary risk: this chunk crosses a table boundary. The `kiconv_gbk_utf8[]` initializer closes at lines 24024-24025, and `kiconv_gbk4_utf8[]` starts at line 24027.
- Previous chunk should cover the earlier `kiconv_gbk_utf8[]` entries through key `0xD9A6`; this chunk continues at `0xD9A7`.
- Next chunk should continue `kiconv_gbk4_utf8[]` at line 25456 with key `0x81319137`, after this chunk ends at `0x81319136`.

### Chunk 4: lines 25456-33002

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb18030_utf8.h lines 25456-33002

## Scope

This report covers lines 25456-33002 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb18030_utf8.h` for `learn_fs` subset A. The slice is entirely inside the `static kiconv_table_array_t kiconv_gbk4_utf8[]` initializer, which begins earlier at line 24027 and maps GB18030 four-byte keys to UTF-8 byte arrays.

The reviewed range contains 7,547 complete mapping rows. It starts at key `0x81319137 -> DA B1` and ends at key `0x81379033 -> E2 92 B7`. The chunk boundary is clean: line 25455 precedes this range with another table row, and line 33003 continues the same table with the next row.

## Public Surface And APIs

This chunk adds data to the kernel-only GB18030-to-UTF-8 conversion table. It introduces no new preprocessor guards, macros, structs, functions, or callable APIs within the line range.

The relevant public/static surface is defined outside the chunk:

- `KICONV_GBK4_UTF8_MAX (39421)` declares the total number of GB18030 four-byte mappings in this file.
- `kiconv_gbk4_utf8[]` is a `static kiconv_table_array_t` table, visible only to translation units that include this header under `_KERNEL`.
- `kiconv_table_array_t` is declared in `kiconv_cck_common.h` as `{ uint32_t key; uchar_t u8[4]; }`.

Rows in this chunk initialize the `key` with a packed four-byte GB18030 code and initialize `u8` with either two or three UTF-8 bytes. The trailing bytes in `u8[4]` rely on normal static zero-fill.

## Control Flow

There is no executable control flow in this chunk. Runtime behavior is supplied by the generic kernel kiconv machinery that consumes this table:

1. GB18030 byte validation is defined separately in `kiconv_sc.h`.
2. A valid four-byte GB18030 sequence is packed into a `uint32_t` key.
3. Conversion code searches `kiconv_gbk4_utf8[]`, using the sorted-key invariant required by `kiconv_binsearch()`.
4. On match, the row's `u8` array is copied to the UTF-8 output.
5. Error handling and replacement behavior are implemented outside this data header.

## State And Dependencies

State in this chunk is immutable static initializer data compiled into any kernel translation unit that includes this header. There is no mutable state, locking, allocation, or I/O.

Dependencies visible from adjacent file context and related headers:

- `_KERNEL` guard controls whether the table declarations are visible.
- `kiconv_table_array_t` and `kiconv_binsearch()` are declared by `uts/common/sys/kiconv_cck_common.h`.
- GB18030 validation and constants live in `uts/common/sys/kiconv_sc.h`.
- `uts/common/sys/Makefile` exports `kiconv_gb18030_utf8.h` and companion `kiconv_utf8_gb18030.h`.
- `uts/common/os/kiconv.c` registers encoding names including `gb18030`, `gbk`, `cp936`, `936`, and `euccn`.

## Risks And Cross-Chunk References

Important invariants: every row must remain syntactically complete, keys must remain sorted for binary search, `KICONV_GBK4_UTF8_MAX` must match the complete table row count across all chunks, and UTF-8 byte arrays must remain valid with zero-filled padding.

Risks visible here include generated-data drift, mid-table chunk boundary mistakes, sparse Unicode ranges after `U+2000` being misread as gaps, and reliance on external validation to reject malformed GB18030 sequences before table lookup.

Previous chunk(s) must account for the file header, guards, macros, the complete two-byte `kiconv_gbk_utf8[]` table, and the start of `kiconv_gbk4_utf8[]`. Next chunk(s) must continue at line 33003 with `0x81379034 -> E2 92 B8`, cover the remaining table rows through line 63449, and verify the closing `_KERNEL`, C++ extern, and header guard structure.

### Chunk 5: lines 33003-40491

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb18030_utf8.h lines 33003-40491

## Scope

This report covers only lines 33003-40491 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb18030_utf8.h` for learn_fs subset A (`Docs/research_subset_a.md`). I read the requested 7,489-line range completely and used adjacent context only to identify the enclosing table declaration, type definition, and neighboring chunk boundaries.

The entire chunk is inside `static kiconv_table_array_t kiconv_gbk4_utf8[]`, the kernel-only GB18030 four-byte-sequence to UTF-8 mapping table that begins at line 24027 and closes much later at line 63449. This chunk contains no standalone declarations, functions, macros, preprocessor branches, or table closing braces.

## APIs And Data Structures

This chunk contributes 7,489 complete `kiconv_table_array_t` initializer rows:

- First row: key `0x81379034` maps to UTF-8 bytes `E2 92 B8` (`U+24B8`).
- Last row: key `0x82338932` maps to UTF-8 bytes `E4 8F 8A` (`U+43CA`).
- The rows are all packed four-byte GB18030 keys mapped to three-byte UTF-8 payloads.

The entry type is defined outside this file in `sys/kiconv_cck_common.h` as `uint32_t key; uchar_t u8[4];`. Every row in this chunk initializes the first three bytes of `u8`; the fourth byte is zero-filled by static aggregate initialization. The full-table count contract is the top-of-file `KICONV_GBK4_UTF8_MAX (39421)`, not redefined in this chunk.

## Control Flow

There is no executable C control flow in this chunk: no functions, branches, loops, calls, allocation, locking, or I/O. Runtime behavior is indirect through the kernel iconv code that consumes `kiconv_gbk4_utf8[]`.

The relevant conversion flow is external to the chunk:

1. GB18030 validation macros in `sys/kiconv_sc.h` define valid byte classes for four-byte sequences: second and fourth bytes are digits `0x30-0x39`, and the third byte is `0x81-0xfe`.
2. Converter code packs a validated four-byte GB18030 sequence into the table key format used here.
3. Shared lookup support declared as `kiconv_binsearch()` in `sys/kiconv_cck_common.h` depends on sorted table keys.
4. On a match, the stored `u8` bytes are emitted according to the UTF-8 length derived by common kiconv code from the first byte.
5. Invalid input handling, replacement-character policy, output-capacity errors, and buffer advancement are implemented in the conversion routines, not in this data range.

## State And Dependencies

The chunk is immutable static kernel data under the file's surrounding `_KERNEL` guard. It has no mutable state and no per-conversion state.

Direct dependencies visible from adjacent context:

- `kiconv_gbk4_utf8[]` declaration at line 24027.
- `kiconv_table_array_t` from `uts/common/sys/kiconv_cck_common.h`.
- `KICONV_GBK4_UTF8_MAX` from this header's top-level constants.
- GB18030 byte-shape macros and plane constants from `uts/common/sys/kiconv_sc.h`.
- Header export through `uts/common/sys/Makefile`.
- Reverse-direction data is separate in `sys/kiconv_utf8_gb18030.h`.

## Data Shape

Mechanical checks over the requested range found:

- Exact rows: 7,489.
- Syntax anomalies: none; every line is a complete table initializer row.
- Key ordering: strictly increasing, with no duplicate or descending keys.
- UTF-8 code point ordering: increasing throughout the chunk.
- Unicode gaps: expected sparse ranges are present around symbol/radical/CJK-extension blocks; these are mapping-table sparsity, not control-flow gaps.

Visible key-prefix spans:

- `0x8137...`: lines 33003-34108, 1,106 rows, `U+24B8..U+299F`, keys `0x81379034..0x8137FE39`.
- `0x8138...`: lines 34109-35368, 1,260 rows, `U+29A0..U+2E90`, keys `0x81388130..0x8138FE39`.
- `0x8139...`: lines 35369-36628, 1,260 rows, `U+2E91..U+34A2`, keys `0x81398130..0x8139FE39`.
- `0x8230...`: lines 36629-37888, 1,260 rows, `U+34A3..U+3993`, keys `0x82308130..0x8230FE39`.
- `0x8231...`: lines 37889-39148, 1,260 rows, `U+3994..U+3E86`, keys `0x82318130..0x8231FE39`.
- `0x8232...`: lines 39149-40408, 1,260 rows, `U+3E87..U+4375`, keys `0x82328130..0x8232FE39`.
- `0x8233...`: lines 40409-40491, 83 rows, `U+4376..U+43CA`, keys `0x82338130..0x82338932`.

## Risks And Cross-Chunk References

The main correctness risks are generated-data risks:

- Count drift: inserting or deleting rows anywhere in the full `kiconv_gbk4_utf8[]` table must keep `KICONV_GBK4_UTF8_MAX` aligned with the complete table.
- Sort-order drift: lookup relies on monotonic keys, so any manual edit must preserve order across chunk boundaries.
- UTF-8 payload drift: consumers trust these byte arrays; malformed triples would be copied directly to output.
- Boundary mistakes: this chunk starts and ends mid-table, so merge/report tooling must not infer a declaration or close brace inside this range.

Cross-chunk continuity:

- Previous chunk ends at line 33002 with key `0x81379033 -> E2 92 B7` (`U+24B7`); this chunk starts at line 33003 with the next row `0x81379034 -> E2 92 B8`.
- Next expected chunk should start at line 40492 with `0x82338933 -> E4 8F 8B` (`U+43CB`), immediately after this chunk's final `0x82338932 -> E4 8F 8A`.
- Later known chunk `47981-55469` remains in the same `kiconv_gbk4_utf8[]` table and continues the generated four-byte mapping data.

### Chunk 6: lines 40492-47980

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb18030_utf8.h lines 40492-47980

## Scope

This chunk is within `sources/os/illumos/illumos-gate`, which is included by `Docs/research_subset_a.md`. The requested line range was read completely.

The range is entirely initializer data inside `static kiconv_table_array_t kiconv_gbk4_utf8[]`, the kernel GB18030 four-byte to UTF-8 mapping table declared earlier in this header. It contains 7,489 mapping entries, starting at line 40492 with packed GB18030 key `0x82338933` mapped to UTF-8 bytes `{ 0xE4, 0x8F, 0x8B }` (`U+43CB`) and ending at line 47980 with key `0x82398231` mapped to `{ 0xEB, 0x8B, 0x92 }` (`U+B2D2`).

## APIs And Data Structures

- No functions, macros, typedefs, or external entry points are defined in this chunk.
- The data extends `kiconv_gbk4_utf8[]`, declared at line 24027 as a `static kiconv_table_array_t` array under the file's `_KERNEL` guard.
- `kiconv_table_array_t` is defined in `sys/kiconv_cck_common.h` as `{ uint32_t key; uchar_t u8[4]; }`.
- The full four-byte table size contract is `KICONV_GBK4_UTF8_MAX` with value `39421`, declared near the top of this same header.
- All entries in this chunk use three-byte UTF-8 payloads stored in the first three slots of `u8[4]`; the fourth array slot is implicit zero-initialized padding.

## Control Flow

There is no executable control flow, allocation, locking, error handling, or buffer movement in this chunk. Runtime behavior is supplied by the kernel kiconv conversion machinery that includes or is generated with these mapping headers.

The relevant runtime flow outside this data is: validate/pack a GB18030 four-byte input sequence, locate the packed key in the sorted `kiconv_gbk4_utf8[]` table, derive output length from the first UTF-8 byte via common UTF-8 length tables, check output capacity, then copy the stored UTF-8 bytes. Invalid input, replacement-character policy, `EILSEQ`/`E2BIG`, and descriptor state are handled outside this chunk.

## State And Data Flow

- Input state represented here is a packed 32-bit GB18030 key in the byte pattern `0x82 0x33..0x39 0x81..0xFE 0x30..0x39`.
- Output state is a fixed inline UTF-8 byte array. In this range the encoded Unicode scalar span is mostly ascending from `U+43CB` through `U+B2D2`.
- A mechanical pass over all 7,489 lines found zero malformed rows and zero GB18030 key-order breaks.
- The GB18030 keys are contiguous according to four-byte GB18030 digit/byte progression: fourth byte `0x30..0x39`, then third byte `0x81..0xFE`, then second byte `0x30..0x39`.
- Unicode scalar values are not perfectly contiguous. There are 21 intentional-looking jumps/skips, including the boundary from `0x82358F32 -> U+4DFF` to `0x82358F33 -> U+9FA6`, which transitions from CJK Extension A-era values into the CJK Unified Ideographs range.

## Dependencies

- Depends on the surrounding header context for CDDL/Unicode licensing, include guards, `_KERNEL`, and optional C++ `extern "C"` wrapping.
- Depends on `sys/kiconv_cck_common.h` for `kiconv_table_array_t`, `uint32_t`, `uchar_t`, `kiconv_binsearch()`, and UTF-8 byte-length helper declarations.
- `usr/src/uts/common/sys/Makefile` lists `kiconv_gb18030_utf8.h` for installation/export with the other kernel iconv headers.
- `usr/src/uts/common/os/kiconv.c` contains the generic kernel iconv registration and common conversion wrappers; it registers the `"gb18030"` encoding name, while this chunk supplies only table data.
- Reverse-direction mapping is separate in `sys/kiconv_utf8_gb18030.h`; this chunk is GB18030/GBK four-byte to UTF-8 only.

## Risks And Cross-Chunk References

- Table ordering is a functional contract. Any edit that breaks sorted key order can break binary-search-style consumers.
- Count drift is a file-level risk: generated or manual edits must keep `KICONV_GBK4_UTF8_MAX` aligned with the full `kiconv_gbk4_utf8[]` table, not this chunk alone.
- Consumers must not assume Unicode scalar contiguity from GB18030 key contiguity; this chunk has visible scalar gaps and jumps.
- Since the table is `static` in a header, each translation unit that includes it can receive a private copy unless build structure constrains inclusion.
- Previous chunk ends at key `0x82338932 -> U+43CA`; this chunk continues immediately at `0x82338933`.
- Next chunk starts at line 47981 with key `0x82398232 -> U+B2D3`, continuing the same table.

### Chunk 7: lines 47981-55469

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb18030_utf8.h lines 47981-55469

## Scope

This chunk is a contiguous middle slice of the illumos kernel GB18030-to-UTF-8 mapping header. It is entirely inside `static kiconv_table_array_t kiconv_gbk4_utf8[]`, the table for GB18030 four-byte sequences. The range contains no function bodies, macros, branches, allocation, or synchronization; its runtime effect is data-driven through the kernel iconv conversion routines that consume this table.

## APIs And Data Structures

- Provides 7,489 `kiconv_table_array_t` entries from GB18030 key `0x82398232` through `0x8334F930`.
- Maps those packed four-byte GB18030 keys to UTF-8 byte sequences from `EB 8B 93` through `ED 80 93`, i.e. Unicode code points `U+B2D3` through `U+D013`.
- The entry type is defined in `sys/kiconv_cck_common.h` as `uint32_t key; uchar_t u8[4];`. In this chunk each initializer supplies a three-byte UTF-8 payload; the fourth byte is zero-filled by C aggregate initialization and is not copied by consumers.
- The table-level count contract is `KICONV_GBK4_UTF8_MAX` near the top of the file, declared as `39421` for the full `kiconv_gbk4_utf8[]` array.

## Control Flow And State

There is no direct control flow in this line range. Runtime control flow is in the kiconv conversion code outside the header: the selected table entry is found by key, `u8_number_of_bytes[first_utf8_byte]` determines how many bytes to copy, output capacity is checked, and then the stored UTF-8 bytes are emitted.

The chunk is stateless read-only kernel data. It does not allocate memory, mutate global state, acquire locks, or retain per-conversion state. Error handling for invalid input, `E2BIG`, replacement characters, and buffer advancement belongs to the conversion routines, not to this table segment.

## Data Shape

- Exact entries read in this chunk: 7,489.
- Key ordering is strictly increasing with no duplicate keys found in this range.
- The GB18030 four-byte key sequence is dense across the chunk: each key follows the previous one by the expected GB18030 four-byte successor rule over digit bytes `0x30`-`0x39` and trail bytes `0x81`-`0xFE`.
- UTF-8 payloads are valid three-byte sequences and increase by exactly one Unicode code point per entry.
- UTF-8 lead-byte transitions visible in the chunk:
  - Line 51354: key `0x8331D735` starts `EC 80 80` (`U+C000`).
  - Line 55450: key `0x8334F731` starts `ED 80 80` (`U+D000`).

## Dependencies

- The header content is only exposed under `_KERNEL`.
- `kiconv_table_array_t` comes from `sys/kiconv_cck_common.h`.
- `usr/src/uts/common/sys/Makefile` exports `kiconv_gb18030_utf8.h` with the other kernel iconv headers.
- Runtime consumers depend on `u8_number_of_bytes[]` from the common Unicode support code to derive the copy length from the first stored UTF-8 byte.
- Reverse-direction UTF-8-to-GB18030 mapping is separate, in `sys/kiconv_utf8_gb18030.h`; this chunk is only for GB18030 four-byte input to UTF-8 output.

## Risks And Cross-Chunk References

- Count drift risk: changing any entries in the full array requires keeping `KICONV_GBK4_UTF8_MAX` aligned with the generated table.
- Ordering risk: lookup code relies on sorted mapping tables; any manual insertion or deletion must preserve monotonic key order across chunk boundaries.
- UTF-8 validity risk: consumers trust table payloads and use only the first byte to decide copy length, so malformed byte triples would propagate directly to callers.
- Boundary continuity: the previous line before this chunk is key `0x82398231` mapping to `U+B2D2`; this chunk starts at `0x82398232` mapping to `U+B2D3`.
- Next chunk continuity: line 55470 continues with key `0x8334F931` mapping to `U+D014`, immediately after this chunk's final key `0x8334F930` mapping to `U+D013`.
- Full-array context: `kiconv_gbk4_utf8[]` begins at line 24027 with a replacement-character sentinel `0x00000000 -> EF BF BD` and the first real key `0x81308130`; it ends near line 63449 before the `_KERNEL` guard closes.

### Chunk 8: lines 55470-62958

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb18030_utf8.h lines 55470-62958

## Scope

This report covers lines 55470-62958 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb18030_utf8.h` for `learn_fs` subset A. The slice is entirely inside the kernel-only `static kiconv_table_array_t kiconv_gbk4_utf8[]` initializer, which begins earlier at line 24027 and maps packed GB18030 four-byte codes to UTF-8 byte arrays.

The reviewed range contains 7,489 complete mapping rows. It starts at key `0x8334F931 -> ED 80 94` (`U+D014`) and ends at key `0x8430F139 -> EF B5 BD` (`U+FD7D`). The chunk boundary is clean: line 55469 is the immediately preceding table row, `0x8334F930 -> ED 80 93`, and line 62959 continues with the next row, `0x8430F230 -> EF B5 BE`.

## Public Surface And APIs

This chunk introduces no macros, type definitions, functions, extern declarations, or standalone APIs. Its only contribution is static initializer data for the existing GB18030 four-byte-to-UTF-8 lookup table.

Relevant declarations outside this chunk:

- `KICONV_GBK4_UTF8_MAX (39421)` declares the total number of four-byte GB18030 mappings in the full table.
- `kiconv_gbk4_utf8[]` is a `static kiconv_table_array_t` table visible only when this header is included under `_KERNEL`.
- `kiconv_table_array_t` is declared in `kiconv_cck_common.h` as `{ uint32_t key; uchar_t u8[4]; }`.

Every row initializes a packed four-byte GB18030 key and a three-byte UTF-8 output sequence. The `u8[4]` field's remaining byte is zero-filled by C aggregate initialization.

## Data Layout

All rows in this chunk follow the same initializer shape:

```c
	0x8334F931,	{ 0xED, 0x80, 0x94 },
```

Observed row properties:

- Mapping rows: 7,489.
- First row: line 55470, `0x8334F931 -> ED 80 94` (`U+D014`).
- Last row: line 62958, `0x8430F139 -> EF B5 BD` (`U+FD7D`).
- Key order: strictly ascending throughout the chunk.
- UTF-8 initializer width: all rows in the requested range use three bytes.
- Format check: no malformed initializer lines were found in the requested range.

The UTF-8 output range is mostly ascending by Unicode code point, but not perfectly contiguous. Important visible transitions:

- Lines 55470-57497 continue dense mappings from `U+D014` through `U+D7FF`, ending immediately before the surrogate range.
- Line 57498 jumps from `U+D7FF` to `U+E76C`, intentionally skipping surrogate code points and earlier private-use code points.
- Lines 57498-57579 contain sparse Private Use Area mappings around `U+E76C` through `U+E865`, with several expected gaps.
- The table later enters compatibility and presentation-form ranges, including CJK compatibility-style output around `U+F900` and following blocks.
- Lines 61874-62107 contain additional sparse compatibility-code-point gaps.
- Lines 62897-62958 continue through `U+FD40`-style presentation forms and end at `U+FD7D`.

## Control Flow

There is no executable control flow in this chunk. Runtime behavior comes from the surrounding kiconv implementation that consumes the table:

1. GB18030 byte validation is defined outside this header, notably by byte-class macros in `kiconv_sc.h`.
2. A valid four-byte GB18030 sequence is packed into a `uint32_t` key.
3. Conversion code searches `kiconv_gbk4_utf8[]`; the strict key ordering preserved here is necessary for binary-search lookup through `kiconv_binsearch()`.
4. On match, the row's `u8` bytes are copied to the output buffer.
5. Buffer-limit handling, replacement behavior, and errno setting are implemented by the converter code and shared kiconv helpers, not by this data table.

This chunk's behavioral role is therefore indirect but important: it preserves a large ordered segment of lookup data for kernel GB18030-to-UTF-8 conversion.

## State And Dependencies

State in this chunk is immutable static initializer data compiled into translation units that include the header. There is no mutable state, locking, allocation, reference counting, I/O, or error handling inside the range.

Dependencies visible from adjacent file context and related headers:

- The enclosing header guard is `_SYS_KICONV_GB18030_UTF8_H`.
- The table declarations are under `_KERNEL`.
- `kiconv_table_array_t` and `kiconv_binsearch()` are declared in `uts/common/sys/kiconv_cck_common.h`.
- GB18030 validation helpers and plane constants live in `uts/common/sys/kiconv_sc.h`, including the four-byte byte-class macros and `KICONV_SC_PLANE1_GB18030_START`.
- `uts/common/sys/Makefile` installs/exports this table header alongside the reverse-direction `kiconv_utf8_gb18030.h`.
- `uts/common/os/kiconv.c` registers GB18030-related encoding names for the kernel iconv subsystem.

## Risks And Invariants

Important invariants for this chunk:

- Every row must remain syntactically complete because the file is a direct C initializer.
- Keys must remain strictly sorted for binary-search consumers.
- `KICONV_GBK4_UTF8_MAX` must match the total row count of the complete `kiconv_gbk4_utf8[]` table, not this chunk's count.
- UTF-8 byte arrays must remain semantically correct; many edits would still compile while silently changing character conversion behavior.
- Gaps in Unicode output are expected in this region and should not be flagged as ordering defects by validators that understand the mapping table.

Risks visible here:

- Generated-data drift: one incorrect key or byte sequence can corrupt conversion for a specific GB18030 character while leaving the table syntactically valid.
- Boundary risk: this chunk starts and ends mid-table, so full validation must include adjacent chunks and the final table terminator.
- Unicode-special-range risk: the dense run stops before surrogate code points, then resumes in private-use and compatibility/presentation blocks; audits must distinguish intentional sparse mapping from missing rows.
- Static-header duplication risk remains a file-level property: because this is a `static` table in a header, including it in multiple kernel translation units can duplicate storage.

## Cross-Chunk References

Previous chunk(s) must account for:

- The license/header guard, `_KERNEL` guard, `KICONV_GBK_UTF8_MAX`, and `KICONV_GBK4_UTF8_MAX`.
- The complete two-byte `kiconv_gbk_utf8[]` table ending at line 24025.
- Start of `kiconv_gbk4_utf8[]` at line 24027.
- Rows before this range, ending immediately before this chunk at line 55469 with `0x8334F930 -> ED 80 93`.

Next chunk(s) must continue with:

- The row after this chunk at line 62959, `0x8430F230 -> EF B5 BE`.
- Remaining `kiconv_gbk4_utf8[]` mappings through the table close at line 63449.
- Closing `_KERNEL`, C++ `extern "C"`, and header guard directives at the end of the file.

### Chunk 9: lines 62959-63457

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb18030_utf8.h lines 62959-63457

## Scope

This chunk covers the final 499 lines of the illumos kernel GB18030-to-UTF-8 mapping header. It is within `sources/os/illumos/illumos-gate`, which is included by `Docs/research_subset_a.md`.

The range is entirely table data plus closing preprocessor/C++ guards. It contains the tail of `static kiconv_table_array_t kiconv_gbk4_utf8[]`, the four-byte GB18030 mapping table declared earlier in the same file. The visible entries map packed four-byte GB18030 keys from `0x8430F230` through `0x8431A439` to three-byte UTF-8 byte sequences from `{ 0xEF, 0xB5, 0xBE }` through `{ 0xEF, 0xBF, 0xBF }`.

## APIs and Entry Points

- No callable functions, macros, or public entry points are defined in this chunk.
- The data belongs to `kiconv_gbk4_utf8[]`, declared earlier as a `static kiconv_table_array_t` array under `#ifdef _KERNEL`.
- The associated size constant visible earlier in the file is `KICONV_GBK4_UTF8_MAX` with value `39421`.
- `kiconv_table_array_t` is defined in `sys/kiconv_cck_common.h` as a `uint32_t key` plus `uchar_t u8[4]`.

## Control Flow

There is no local control flow. Runtime behavior is supplied by conversion code elsewhere that includes this header and searches or indexes the static table.

The table is ordered by ascending packed GB18030 key. Within most subranges, UTF-8 bytes advance monotonically, but this chunk also shows intentional mapping gaps and jumps, such as `0x84318538` to `0x84318539`, `0x84319534` to `0x84319535`, and `0x8431A233` to `0x8431A234`.

## State and Data Flow

- Input state is encoded as a packed 32-bit GB18030 four-byte key.
- Output state is an inline UTF-8 byte array; all visible mappings emit three-byte UTF-8 sequences beginning with `0xEF`.
- The final data entry is `0x8431A439 -> { 0xEF, 0xBF, 0xBF }`, followed by `};`.
- The chunk closes `_KERNEL`, the optional C++ `extern "C"` block, and `_SYS_KICONV_GB18030_UTF8_H`.

## Dependencies

- Depends on `kiconv_table_array_t`, `uint32_t`, and `uchar_t`.
- Depends on consumers honoring `KICONV_GBK4_UTF8_MAX` and sorted key order.
- The table is only visible under `_KERNEL`.
- Direct non-header references to `kiconv_gbk4_utf8` were not visible in the searched paths; consumers are likely include-time users of this static header data.

## Risks and Edge Cases

- `static` table data in a header can duplicate storage per including translation unit.
- The table reaches UTF-8 encodings for upper `U+FFxx` values through `U+FFFF`; policy validation, if required, must happen outside this table.
- Lookup code must not infer contiguous Unicode progression because visible jumps skip reserved/unmapped ranges.
- The fourth `u8[4]` byte is implicitly zero for these three-byte mappings and should be treated as padding/terminator-like state, not payload.

## Cross-Chunk References

- Earlier chunks define the header guards, constants, `kiconv_gbk_utf8[]`, and earlier portions of `kiconv_gbk4_utf8[]`.
- Adjacent preceding lines continue the same table and lead into this chunk at `0x8430F230`.
- This chunk closes the four-byte table and the file; no later chunks remain for this source file.
- The final per-file report should merge this with earlier chunk reports rather than deriving file-level behavior from this tail alone.
