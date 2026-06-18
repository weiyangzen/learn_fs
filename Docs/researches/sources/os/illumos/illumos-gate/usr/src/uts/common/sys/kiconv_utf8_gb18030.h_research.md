# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_gb18030.h

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-11564, source bytes 262129, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_utf8_gb180_8c3e6c55d1f9_research.md`
- chunk 2: lines 11565-23674, source bytes 262126, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_utf8_gb180_40d67577ad8f_research.md`
- chunk 3: lines 23675-37471, source bytes 262143, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_utf8_gb180_b43910e0740f_research.md`
- chunk 4: lines 37472-49451, source bytes 262128, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_utf8_gb180_cd9899b98bc8_research.md`
- chunk 5: lines 49452-61208, source bytes 262139, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_utf8_gb180_71fe82cb3480_research.md`
- chunk 6: lines 61209-63451, source bytes 50785, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_utf8_gb180_1e9eeacd7573_research.md`

## Chunk Research

### Chunk 1: lines 1-11564

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_gb18030.h lines 1-11564

## Scope

This chunk covers the start of `kiconv_utf8_gb18030.h`, from the license and include guards through the first 11,483 entries of the UTF-8 to GB18030 kernel conversion table. The chunk ends in the middle of the table at line 11564, so the array terminator, `_KERNEL` close, C++ linkage close, and outer include-guard close are cross-chunk dependencies.

## Purpose and APIs

- Defines `KICONV_UTF8_GB18030_MAX` as `63361`, the whole-file maximum mapping number from UTF-8 to GB18030.
- Starts `static kiconv_table_t kiconv_utf8_gb18030[]`.
- Each row maps a packed UTF-8 byte sequence key to a packed GB18030 value.
- First row is a special/default mapping: `0x0000 -> 0x0000003F`, commented as non-identical conversion fallback.

## Control Flow and State

There is no runtime control flow in this chunk. Its behavior is compile-time table data guarded by `_KERNEL`.

Visible structure:

- Outer include guard: `_SYS_KICONV_UTF8_GB18030_H`.
- Optional C++ `extern "C"` wrapping.
- Kernel-only macro and table under `#ifdef _KERNEL`.
- The table remains open at the chunk boundary.

Visible data properties:

- 11,483 table entries in this chunk.
- 11,035 mappings produce four-byte GB18030 values.
- 448 mappings produce two-byte GB/GBK-compatible values.
- Keys are strictly increasing in the visible range.
- Coverage runs from special `0x0000`, then UTF-8 `0xC280` through `0xE2B599` / Unicode U+0080 through U+2D59.

## Dependencies

- Requires `kiconv_table_t`, defined in `kiconv_cck_common.h` as `{ uint32_t key; uint32_t value; }`.
- Depends on including kernel conversion infrastructure for integer types and lookup/serialization behavior.
- Installed with related kernel iconv headers via `usr/src/uts/common/sys/Makefile`.
- Related files include `kiconv_gb18030_utf8.h` for reverse mapping and `kiconv_sc.h` for GB18030 byte validation helpers.

## Risks

- Consumers likely depend on sorted keys for lookup; visible entries satisfy that invariant.
- `KICONV_UTF8_GB18030_MAX` is not the chunk count.
- The static header table can create private copies in each including translation unit.
- Packed integer values require correct byte-count and byte-order serialization by conversion code.
- Generated table edits are high-risk; validation should check sorted keys, counts, sentinel, final closure, and representative mappings.

## Cross-Chunk References

- Later chunks must close `kiconv_utf8_gb18030[]`.
- Later chunks must verify the final entry and total count against `KICONV_UTF8_GB18030_MAX`.
- Later chunks must confirm ordering continues after `0xE2B599`.
- Later chunks contain the closing `_KERNEL`, C++ linkage, and include-guard directives.

### Chunk 2: lines 11565-23674

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_gb18030.h lines 11565-23674

## Scope

This report covers only chunk 2 of the oversized illumos kernel header `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_gb18030.h`, lines 11565-23674, within learn_fs subset A (`Docs/research_subset_a.md`). The range was read completely. Adjacent context was used only to identify the enclosing declaration, shared table type, and kiconv registry context.

The chunk is entirely initializer data inside `static kiconv_table_t kiconv_utf8_gb18030[]`; it starts mid-array at `0xE2B59A -> 0x8138E034` and ends mid-array at `0xE5B2A7 -> 0x8CFD`.

## APIs And Exported Data

No callable API, macro, typedef, or externally linked symbol is defined in this chunk. The exported behavior is data-driven through the enclosing static table:

- The table is declared earlier in the file under `#ifdef _KERNEL`.
- `KICONV_UTF8_GB18030_MAX` is defined earlier as `63361`.
- Each row is a `kiconv_table_t` pair from `sys/kiconv_cck_common.h`: `uint32_t key` and `uint32_t value`.
- `key` is a UTF-8 byte sequence packed into a 32-bit integer.
- `value` is a GB18030 result packed into a 32-bit integer; values with four encoded bytes use eight hex digits, while two-byte GBK/GB18030 compatibility results use four hex digits.

This chunk contributes 12,110 mapping rows. I counted 8,009 four-byte GB18030 mappings and 4,101 two-byte mappings. The first two-byte entry in this chunk is `0xE2BA81 -> 0xFE50` at line 11860; the last four-byte entry in this chunk is `0xE4B7BF -> 0x82358F32` at line 19922; after line 19923 the visible range is the CJK ideograph section represented here by two-byte GB mappings through `0x8CFD`.

## Control Flow

There is no local control flow: no functions, branches, loops, allocations, locking, or error handling appear in the assigned range. Runtime conversion control flow is supplied by kiconv converter code that includes or otherwise compiles this table and searches it.

The only control-relevant property inside the chunk is ordering. Rows are sorted by ascending packed UTF-8 key. There are normal packed-UTF-8 discontinuities at byte-boundary transitions, such as `0xE2B5BF -> 0xE2B680`, and larger range transitions such as `0xE2BFBF -> 0xE38080`; these are expected for UTF-8 byte encoding and Unicode block coverage, not executable branches.

## State And Data Flow

The chunk contributes immutable kernel conversion state. A caller's decoded/packed UTF-8 input key flows into a table lookup; the corresponding table value becomes the emitted GB18030 byte sequence.

Visible data-flow patterns:

- Lines 11565-11859 continue dense four-byte GB18030 algorithmic mappings in the `0x8138...` region.
- Lines 11860-19922 mix four-byte mappings with selected two-byte compatibility mappings, including `0xFExx`, `0xA1xx`, `0xA2xx`, `0xA4xx`, `0xA5xx`, and other GB ranges.
- Line 19923 enters common CJK ideograph mappings, beginning `0xE4B880 -> 0xD2BB`; from there through line 23674 this chunk's visible entries are two-byte GB values.
- The visible packed UTF-8 key range runs from `0xE2B59A` through `0xE5B2A7`.

No mutable state is updated by the table itself. Because the enclosing array is `static` in a header, storage is internal to each translation unit that includes it with `_KERNEL` enabled.

## Dependencies

Direct dependencies visible from adjacent context are:

- `kiconv_table_t` from `sys/kiconv_cck_common.h`.
- `_KERNEL`, which gates the table declaration.
- Consumers honoring `KICONV_UTF8_GB18030_MAX` and the sorted key invariant.
- Header installation/listing through `uts/common/sys/Makefile`.
- Charset-name registration context in `uts/common/os/kiconv.c`, where `gb18030` is listed as a normalized code name.

The checked tree did not show a direct C source reference to the `kiconv_utf8_gb18030` symbol outside this generated header; the table is likely consumed through generated or build-selected kiconv module include paths.

## Risks And Edge Cases

The main correctness risk is silent data corruption from a bad literal, missing row, duplicate key, or sort-order break. Since conversion is table-driven, a single row error can affect file names or strings converted under GB18030 locales without any local runtime check in this header.

Lookup code must distinguish two-byte and four-byte output values from the packed integer form. Values such as `0xFE50` and `0x8138E034` are both stored in the same `uint32_t value` field, so consumers must already know how to emit the correct number of bytes.

Four-byte GB18030 values in this chunk follow the byte-shape constraints for GB18030 sequences: first byte `0x81`-`0x84`, second byte `0x30`-`0x39`, third byte `0x81`-`0xFE`, fourth byte `0x30`-`0x39`. Two-byte values are interspersed before the ideograph-heavy tail, so code must not assume a single output width over the chunk.

The `static` header table can duplicate a large amount of read-only data if included by multiple kernel translation units. The file-level merge should check whether this is an established pattern across sibling kiconv headers rather than treating it as a local anomaly.

## Cross-Chunk References

This is chunk 2 of 6 for `kiconv_utf8_gb18030.h` according to `Docs/researches/chunk_manifest.tsv`.

- Chunk 1 contains the license/header guards, `KICONV_UTF8_GB18030_MAX`, the `kiconv_utf8_gb18030[]` declaration, the special non-identical conversion entry, and earlier UTF-8-to-GB18030 mappings through line 11564.
- This chunk continues the same array from line 11565 to line 23674 and ends mid-table after `0xE5B2A7 -> 0x8CFD`.
- Chunk 3 begins at line 23675 and should continue the CJK ideograph section.
- Later chunks continue and eventually close the array and preprocessor guards.

The reverse-direction data lives in `kiconv_gb18030_utf8.h`; common table types and helper prototypes live in `kiconv_cck_common.h`; charset registration context is in `uts/common/os/kiconv.c`.

### Chunk 3: lines 23675-37471

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_gb18030.h lines 23675-37471

## Scope

This report covers only lines 23675-37471 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_gb18030.h` for learn_fs subset A (`Docs/research_subset_a.md`). I read the full requested range and used adjacent context only to identify the enclosing declarations, shared type definitions, and nearby conversion infrastructure.

The entire chunk is an interior slice of the kernel-only UTF-8-to-GB18030 mapping table:

- The file declares `KICONV_UTF8_GB18030_MAX` as `63361`.
- The enclosing array is `static kiconv_table_t kiconv_utf8_gb18030[]`, declared earlier under `#ifdef _KERNEL`.
- This chunk contributes 13,797 table entries and does not open or close the array.

## APIs And Exported Data

No callable API, macro, typedef, function pointer, or public kernel entry point is defined in this line range. The host-visible surface is data: packed UTF-8 keys and packed GB18030 values consumed by converter code that includes this header.

Each entry is a `kiconv_table_t` pair from `sys/kiconv_cck_common.h`:

- `key`: a UTF-8 byte sequence packed into a `uint32_t`.
- `value`: the GB18030 output sequence packed into a `uint32_t`.

The chunk starts with `0xE5B2A8 -> 0x8CFE` at line 23675 and ends with `0xE98A8C -> 0xE386` at line 37471. Decoding the packed UTF-8 bytes, this is the contiguous Unicode code point span U+5CA8 through U+928C. The adjacent previous line is U+5CA7, and the adjacent next line is U+928D, confirming this chunk is a middle segment of a larger ordered table.

## Control Flow

There is no local runtime control flow: no branches, loops, calls, allocation, locking, error handling, or state mutation occur in this chunk.

Runtime behavior is supplied by converter glue outside this range. Adjacent common declarations expose `kiconv_binsearch()` and UTF-8-to-CCK wrapper prototypes for tables of this shape. The practical invariant for this chunk is therefore ordering by `key`: the 13,797 entries are monotonically increasing by packed UTF-8 key, which supports binary-search based lookup. The mapped `value` field is not monotonic and must not be searched or range-inferred.

## State And Data Flow

This chunk contributes immutable static mapping state. Because the array is declared `static` in a header, storage is internal to any including translation unit rather than exported as one global object.

Data-flow semantics are one-way:

- Input to lookup is a validated UTF-8 sequence packed into a 24-bit value in a `uint32_t`.
- Successful lookup returns the packed GB18030 value in the table entry.
- Missing keys, invalid UTF-8, replacement policy, output-buffer sizing, and errno behavior are handled by converter code outside this table.

All 13,797 visible output values are four hex digits, so this slice maps to two-byte GB18030/GBK-compatible sequences only. Mechanical checks found no four-byte GB18030 values in the chunk, no malformed entry lines, no duplicate/decreasing keys, and no invalid two-byte GB18030 byte forms: first bytes are in `0x81`-`0xfe`, and second bytes avoid `0x7f` while staying in the valid `0x40`-`0x7e` or `0x80`-`0xfe` ranges.

The output values mix extension/private mapping ranges such as `0x8D40`-style assignments with standard-looking two-byte CJK values such as `0xD1D2`, `0xC1EB`, `0xB0B6`, and `0xE1B6`. This means callers must treat the table as authoritative per-entry mapping data, not as a formula from Unicode scalar position to GB18030 bytes.

## Dependencies

Direct dependencies visible from adjacent context:

- `_KERNEL` gates the table; non-kernel builds do not see this data.
- `kiconv_table_t` is defined in `sys/kiconv_cck_common.h` as `{ uint32_t key; uint32_t value; }`.
- The file header attributes the mapping data to Unicode data modified by Sun Microsystems.
- `uts/common/sys/Makefile` lists `kiconv_utf8_gb18030.h` among installed/common system headers.

Related converter context:

- `sys/kiconv_cck_common.h` declares `kiconv_binsearch()`, `kiconv_utf8_to_cck()`, and `kiconvstr_utf8_to_cck()` as common UTF-8-to-CCK conversion helpers.
- `uts/common/os/kiconv.c` registers `gb18030` as a normalized charset name with code id `9`.
- The reverse mapping lives in `kiconv_gb18030_utf8.h`; this chunk alone does not prove round-trip completeness.

Direct C references to `kiconv_utf8_gb18030` outside this header were not visible in the searched tree, so include-time/generated use should be checked when merging the final per-file report.

## Risks And Edge Cases

- Lookup correctness depends on sorted `key` order. Any duplicate, deletion, or out-of-order insertion can break binary-search behavior or silently select the wrong character.
- `KICONV_UTF8_GB18030_MAX` must continue to match the full table, not this chunk count.
- A single mistyped literal can corrupt path/name conversion under GB18030 locales without causing compile-time failure.
- Since the table is `static` in a header, each including translation unit can carry its own copy, increasing kernel text/data footprint if included broadly.
- The output values are all two-byte mappings in this range; callers still need separate handling for ASCII passthrough, four-byte GB18030 mappings in other chunks, invalid UTF-8, incomplete input, and replacement-character policy.
- The chunk maps a large contiguous Unicode range, but GB18030 output bytes are intentionally sparse and non-monotonic; compression or regeneration must preserve exact per-codepoint values.

## Cross-Chunk References

- Earlier chunks define the file prologue, licensing/provenance comments, header guards, `_KERNEL` gate, `KICONV_UTF8_GB18030_MAX`, and the start of `kiconv_utf8_gb18030[]`.
- The immediately preceding data line maps U+5CA7 (`0xE5B2A7`) to `0x8CFD`; this chunk begins at U+5CA8.
- The immediately following data line maps U+928D (`0xE98A8D`) to `0xE387`; later chunks continue the same table.
- The final per-file report should merge this middle-table segment with other chunks before drawing file-wide conclusions about total table size, closing guards, and complete UTF-8/GB18030 coverage.

### Chunk 4: lines 37472-49451

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_gb18030.h lines 37472-49451

## Scope

This report covers only `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_gb18030.h` lines 37472-49451 in learn_fs subset A (`Docs/research_subset_a.md`). I read the requested range completely and used adjacent context only to identify the enclosing declaration, table type, guards, and registration context. This chunk is generated/static kernel character-conversion data, not executable filesystem or VFS logic.

## APIs And Exported Data

The chunk is a middle slice of the `_KERNEL`-only `static kiconv_table_t kiconv_utf8_gb18030[]` initializer declared near the top of the file. Adjacent context defines `KICONV_UTF8_GB18030_MAX` as `63361`; this chunk contributes 11,980 table entries.

Each entry is a `kiconv_table_t` pair:

- `key`: a UTF-8 byte sequence packed into a `uint32_t`.
- `value`: the GB18030 output sequence packed into a `uint32_t`; values in this chunk are either two-byte GBK/GB18030 compatibility values or four-byte GB18030 sequences.

The exact requested range starts at `0xE98A8D -> 0xE387` and ends at `0xEC8598 -> 0x8331F939`. Lines 37472-40824 contain 3,353 two-byte destination mappings, ending with `0xE9BEA5 -> 0xFD9B`. Lines 40825-49451 contain 8,627 four-byte destination mappings, starting at `0xE9BEA6 -> 0x82358F33`.

## Control Flow

There are no functions, branches, loops, lock operations, allocations, or direct runtime side effects in this line range. Runtime behavior is indirect: common kiconv conversion code can binary-search or otherwise consult this sorted table when converting packed UTF-8 input to GB18030 bytes.

The only control-affecting structure is outside this chunk: the whole array is under `_KERNEL`, with C++ linkage guards and include guards around the header. Because the table is declared `static`, including translation units receive internal-linkage table storage rather than an exported global symbol.

## State And Dependencies

This chunk contributes immutable lookup-table state to the UTF-8-to-GB18030 converter. It depends on `kiconv_table_t` from `sys/kiconv_cck_common.h`, defined as two `uint32_t` fields (`key` and `value`). Adjacent common declarations also expose `kiconv_utf8tocck_t`, UTF-8-to-CCK wrapper prototypes, and `kiconv_binsearch()`, which explains why sorted packed keys matter.

The source file is listed for installation in `usr/src/uts/common/sys/Makefile`, and `usr/src/uts/common/os/kiconv.c` registers `gb18030` as a known code name. A repository-wide search in the checked-in tree found no direct `.c` reference to `kiconv_utf8_gb18030` or `KICONV_UTF8_GB18030_MAX` outside this header, so the concrete include/generator path is not visible in this chunk alone.

## Risks

The main correctness risks are data risks: an incorrect literal can silently corrupt GB18030 conversion for affected Unicode code points; an unsorted key, duplicate key, or missing key can break binary-search-based lookup; and a mismatch between the actual table size and `KICONV_UTF8_GB18030_MAX` can cause incomplete searches or out-of-bounds reads in consumers.

The two-byte to four-byte transition at lines 40824-40825 is a useful audit boundary. Any regeneration or hand edit should preserve ascending UTF-8 keys across that boundary and maintain GB18030 sequence legality, especially the four-byte byte-class constraints encoded by values such as `0x82358F33` through `0x8331F939`.

## Cross-Chunk References

This chunk continues the same array from earlier chunks and ends mid-array. The next chunk begins at line 49452 with `0xEC8599 -> 0x8331FA30`, continuing the four-byte GB18030 sequence run. The prior chunk should end at line 37471 with `0xE98A8C -> 0xE386`, immediately before this chunk's first key.

Related files visible from adjacent context are `kiconv_cck_common.h` for the shared table type and wrapper contracts, `kiconv_gb18030_utf8.h` for the reverse-direction mapping table, `uts/common/os/kiconv.c` for charset-name registration, and `uts/common/sys/Makefile` for header listing.

### Chunk 5: lines 49452-61208

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_gb18030.h lines 49452-61208

## Scope

This report covers only `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_gb18030.h` lines 49452-61208 for learn_fs subset A (`Docs/research_subset_a.md`). I read the requested range completely and used adjacent context only to identify the enclosing declaration, type, guards, whole-table count, and neighboring chunk boundaries.

The chunk is entirely inside the kernel-only `static kiconv_table_t kiconv_utf8_gb18030[]` initializer declared earlier in the file. It contains 11,757 mapping rows and no declarations, functions, macros, comments, or preprocessor directives of its own.

## APIs And Exported Data

No callable API is defined in this range. The chunk contributes immutable entries to `kiconv_utf8_gb18030[]`, whose adjacent context defines:

- `KICONV_UTF8_GB18030_MAX (63361)`, the full row-count contract for the table.
- `kiconv_utf8_gb18030[]`, a `static kiconv_table_t` array compiled only under `_KERNEL`.
- `kiconv_table_t`, from `sys/kiconv_cck_common.h`, as `{ uint32_t key; uint32_t value; }`.

Each row maps a packed UTF-8 byte sequence in `key` to a packed GB18030 byte sequence in `value`. This chunk starts at `0xEC8599 -> 0x8331FA30` and ends at `0xEF9D85 -> 0x8339D238`.

## Data Covered

Structural checks over the requested line range found:

- 11,757 initializer rows; every line matches the same `0xKEY, 0xVALUE,` shape.
- UTF-8 key range: `0xEC8599` through `0xEF9D85`.
- GB18030 value range by numeric value: minimum two-byte value `0xA140`, maximum four-byte value `0x8339D238`.
- No duplicate UTF-8 keys and no duplicate GB18030 values inside the chunk.
- GB18030 value widths: 9,689 four-byte mappings and 2,068 two-byte mappings.
- UTF-8 leading-byte distribution: `0xEC` 3,751 rows, `0xED` 2,048 rows, `0xEE` 4,096 rows, `0xEF` 1,862 rows.

Most entries are algorithmic GB18030 four-byte mappings in ranges beginning with `0x8331` through `0x8339`. The chunk also contains substantial two-byte compatibility mappings. Visible examples include the transition from `0xED9FBF -> 0x8336C738` to `0xEE8080 -> 0xAAA1`, the later wrap from `0xEE9385 -> 0xFEFE` to `0xEE9386 -> 0xA140`, and mixed private-use/compatibility runs around `0xEE9Dxx` through `0xEEA1xx`.

## Control Flow

There is no local executable control flow: no branches, loops, calls, allocations, locks, or mutable operations appear in this chunk.

Runtime behavior is supplied by the generic kernel kiconv code outside this header. Adjacent common declarations expose `kiconv_binsearch()` and UTF-8-to-CCK wrapper functions that operate on `kiconv_table_t` arrays. The chunk therefore participates in conversion by being searched for a packed UTF-8 key; on match, the paired GB18030 value is emitted by converter glue outside this file.

The UTF-8 key side is sorted by encoded byte sequence, which is a behavioral invariant for binary-search use. Apparent UTF-8 numeric jumps such as `0xEC85BF -> 0xEC8680` are normal UTF-8 byte-sequence progression that skips invalid continuation-byte forms. GB18030 values are not globally sorted because the table is keyed by UTF-8, and because standard two-byte mappings interrupt the generated four-byte ranges.

## State And Dependencies

The only state in this chunk is immutable static initializer data. Because the array is declared `static` in a header, each including kernel translation unit can receive its own internal-linkage copy.

Direct dependencies and surrounding contracts:

- `_KERNEL` must be defined for the enclosing table to exist.
- `kiconv_table_t`, `uint32_t`, and related kernel integer typedefs must be available before this header's table declaration.
- Common UTF-8 validation and conversion wrapper declarations live in `sys/kiconv_cck_common.h`.
- The header is listed with related kiconv data headers in `uts/common/sys/Makefile`.
- Charset-name registration for `gb18030` is visible in `uts/common/os/kiconv.c`, while this table is the UTF-8-to-GB18030 data payload.
- The reverse-direction mapping is in `kiconv_gb18030_utf8.h`; it should be considered a companion table, not a proof that every mapping here round-trips identically.

## Risks And Invariants

Important invariants:

- The full table must retain exactly `KICONV_UTF8_GB18030_MAX` rows.
- Rows must remain sorted by `key`, not by GB18030 `value`.
- Packed literals must preserve byte order expected by the converter.
- Two-byte and four-byte GB18030 values must both be handled correctly by output code; this chunk contains both forms.

Risks:

- Manual edits are high-risk because one wrong literal silently changes kernel filename/string conversion in GB18030 locales.
- Sorting by the wrong field would break lookup despite making the GB18030 side look cleaner.
- Naive validators may misclassify the `0xEE...` private-use UTF-8 key range or the mixed two-byte GB18030 compatibility values as anomalies; they are intentional mapping data.
- The `static` header table can duplicate a large amount of read-only data if included broadly.
- The chunk begins and ends mid-array, so it cannot independently verify opening guards, closing guards, or whole-file row count without adjacent chunks.

## Cross-Chunk References

- Earlier chunks define the license/header guards, `_KERNEL` gate, `KICONV_UTF8_GB18030_MAX`, and the start of `kiconv_utf8_gb18030[]`.
- The immediately preceding line before this chunk maps `0xEC8598 -> 0x8331F939`; this chunk continues at `0xEC8599 -> 0x8331FA30`.
- The next chunk begins at line 61209 with `0xEF9D86 -> 0x8339D239` and later closes the table and file guards at the end of the source file.
- Common conversion semantics should be merged from `kiconv_cck_common.h` research and cross-checked with the companion reverse table `kiconv_gb18030_utf8.h`.

### Chunk 6: lines 61209-63451

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_gb18030.h lines 61209-63451

## Scope

This report covers only `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_gb18030.h` lines 61209-63451 in learn_fs subset A (`Docs/research_subset_a.md`). I read the requested range completely and used adjacent context only to identify the enclosing table declaration, type definition, preprocessor guards, and nearby kiconv registration context. This chunk is static kernel character-conversion data, not executable control logic.

## APIs And Exported Data

The chunk is the final portion of the `static kiconv_table_t kiconv_utf8_gb18030[]` initializer declared at line 81 under `#ifdef _KERNEL`. Adjacent context defines `KICONV_UTF8_GB18030_MAX` as `63361`; this slice contributes 2,234 mapping entries and then closes the table and header guards at lines 63443-63451.

Each entry is a two-field `kiconv_table_t` pair:

- `key`: a UTF-8 byte sequence packed into a `uint32_t`, such as `0xEF9D86`.
- `value`: the GB18030 result packed into a `uint32_t`; most entries here are four-byte GB18030 sequences, with selected two-byte GBK/GB18030 compatibility values.

The exact chunk boundary starts at `0xEF9D86 -> 0x8339D239` and ends at `0xEFBFBF -> 0x8431A439`. Notable embedded two-byte mapping runs include `0xFD9C`-`0xFDA0`, `0xFE40`-`0xFE4F`, CJK punctuation-style values in the `0xA6xx` and `0xA9xx` ranges, fullwidth ASCII mappings `0xEFBC81`-`0xEFBD9E` mostly to `0xA3A1`-`0xA3FD`, and final special mappings around `0xEFBFA0`-`0xEFBFA5`.

## Control Flow

There are no functions, branches, loops, allocations, locks, or runtime side effects in this chunk. The only control-affecting syntax is preprocessor structure: the array is compiled only for `_KERNEL`, and the file closes its C++ `extern "C"` and include guards after the initializer.

Runtime conversion behavior is indirect. Adjacent common kiconv declarations define `kiconv_table_t`, `kiconv_binsearch()`, and UTF-8-to-CCK wrapper functions that operate on mapping tables of this shape. `kiconv.c` registers `gb18030` as a normalized code name with code id `9`, but this checked-in tree does not show a direct C include of this specific generated header outside the header list in `uts/common/sys/Makefile`.

## State And Dependencies

The chunk contributes immutable static table state in every kernel translation unit that includes the header with `_KERNEL` set. Because the symbol is `static`, linkage is internal to the including translation unit rather than a shared exported object.

Direct dependencies are:

- `kiconv_table_t` from `sys/kiconv_cck_common.h`, a `{ uint32_t key; uint32_t value; }` pair.
- The `_KERNEL` preprocessor gate surrounding the table.
- Header installation/listing through `uts/common/sys/Makefile`.
- Unicode/GB18030 mapping data provenance noted in the file header.

The table is sorted by ascending packed UTF-8 key in this chunk, matching binary-search expectations visible in common kiconv declarations.

## Risks And Cross-Chunk References

A single wrong literal can silently produce incorrect filename or string conversion for GB18030 locales. The main risks are table drift from the authoritative mapping source, broken sort order, duplicate or missing UTF-8 keys, and mismatches between `KICONV_UTF8_GB18030_MAX` and the actual table size used by converter glue.

This is a continuation from previous chunks of the same oversized header: it starts mid-array after earlier UTF-8-to-GB18030 mappings and closes the array and file. There is no later chunk for this file after line 63451. Cross-file context for the reverse direction is `kiconv_gb18030_utf8.h`; common table semantics and conversion wrappers are in `kiconv_cck_common.h`, while charset-name registration is visible in `uts/common/os/kiconv.c`.
