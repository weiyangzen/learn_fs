# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_euctw.h

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-13007, source bytes 262135, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_utf8_euctw_376b56891390_research.md`
- chunk 2: lines 13008-25996, source bytes 262136, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_utf8_euctw_47b83b287746_research.md`
- chunk 3: lines 25997-37911, source bytes 262130, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_utf8_euctw_c1bbc0b0b16c_research.md`
- chunk 4: lines 37912-49826, source bytes 262130, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_utf8_euctw_3f47fe2c0ceb_research.md`
- chunk 5: lines 49827-55539, source bytes 125580, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_utf8_euctw_70711169f840_research.md`

## Chunk Research

### Chunk 1: lines 1-13007

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_euctw.h lines 1-13007

## Scope

This report covers only `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_euctw.h` lines 1-13007 in learn_fs subset A (`Docs/research_subset_a.md`). I read the requested range completely. Adjacent context was used only to confirm that line 13008 continues the same table initializer and to identify shared kiconv type/API declarations.

The chunk is generated/static kernel character-conversion data, not executable conversion logic. It begins the UTF-8 to EUC-TW/CNS 11643 mapping header and stops mid-initializer.

## APIs And Exported Data

This chunk defines the public header guard and kernel-only table data:

- `_SYS_KICONV_UTF8_EUCTW_H`: include guard for the header.
- `extern "C"` wrapping for C++ inclusion.
- `#ifdef _KERNEL`: all conversion declarations/data in this chunk are kernel-only.
- `KICONV_UTF8_EUCTW_MAX` as `55442`, the stated maximum mapping count for UTF-8 to EUC-TW.
- `static kiconv_table_t kiconv_utf8_euctw[]`: a file-local table when included into a kernel translation unit. The chunk starts the initializer at line 88 and includes 12,919 mapping rows through line 13007.

`kiconv_table_t` is defined in `kiconv_cck_common.h` as two `uint32_t` fields: `key` and `value`. In this table, `key` is a packed UTF-8 byte sequence represented as a hexadecimal integer, and `value` is a packed EUC-TW/CNS 11643 destination code. The first row is a special non-identical conversion entry:

- `0x0000 -> 0x0003F`, mapping the sentinel/non-identical input to ASCII question mark.

The table comment documents the data source and limitations: Unicode 3.2, `Unihan-3.2.0.txt`, CNS 11643 mapping, with some missing characters and no CNS11643-92 support.

## Data Shape

The included rows are sorted in nondecreasing packed UTF-8 key order, which matches the shared `kiconv_binsearch()` contract. The first and last entries in this chunk are:

- line 89: `0x0000 -> 0x0003F`
- line 13007: `0xE6AA85 -> 0x2DDB4`

The next chunk continues immediately at line 13008 with `0xE6AA86`, so this chunk does not close the array.

The chunk covers:

- Prologue, licensing, guard, and declaration setup on lines 1-88.
- Non-Han symbols and punctuation early in the table, including Greek, math symbols, arrows, box drawing, circled numbers, kana, and compatibility forms.
- CJK Extension A before the core CJK block.
- The transition into core CJK Unified Ideographs at line 6309 with `0xE4B880 -> 0x1C4A1`.
- Core CJK mappings through `0xE6AA85`.

Observed row counts and properties for lines 1-13007:

- 13,007 lines total.
- 12,919 table rows.
- Values are all five hex digits after `0x` in this range, including the sentinel `0x0003F`.
- Destination high nibbles observed: `0`, `1`, `2`, `3`, `4`, `5`, `6`, `7`, and `F`, indicating this chunk already spans multiple CNS/EUC-TW destination groups and compatibility/private mapping cases.
- One duplicate key is visible: `0xE58D84` appears on lines 7519 and 7520 with two different destination values, `0x1A4BF` and `0x3A1B8`.

## Control Flow

There are no functions, branches, loops, allocations, locks, or runtime side effects in this chunk. Runtime behavior is indirect:

1. A UTF-8 to CCK/EUC-TW converter reads bytes and packs a valid UTF-8 sequence into a `uint32_t` key.
2. The converter searches `kiconv_utf8_euctw` with the shared `kiconv_binsearch(uint32_t key, void *tbl, size_t nitems)` API declared in `kiconv_cck_common.h`.
3. If found, the packed destination value is emitted as EUC-TW bytes by the including conversion module.
4. If absent, the common wrapper path handles invalid or unmappable input according to kiconv flags and errno behavior.

The chunk itself only provides the data needed by that lookup path.

## State And Dependencies

All state in this chunk is static compiled data. Because the array is declared `static` in a header, each including translation unit gets its own internal-linkage copy rather than a single external symbol.

Direct dependencies visible or confirmed from adjacent common headers:

- `_KERNEL` controls whether the table is visible.
- `kiconv_table_t` from `sys/kiconv_cck_common.h`.
- `uint32_t` as the storage type for packed keys and values.
- Common CCK conversion APIs: `kiconv_binsearch()`, `kiconv_utf8_to_cck()`, and `kiconvstr_utf8_to_cck()`.
- Kernel encoding registry recognizes `"euctw"` as code id `16` in `uts/common/os/kiconv.c`.
- `uts/common/sys/Makefile` installs/lists both `kiconv_utf8_euctw.h` and the reverse `kiconv_euctw_utf8.h`.

Licensing dependencies are also explicit: CDDL for illumos/Sun code and Unicode data-file permission text.

## Risks And Edge Cases

The table is data-critical: a wrong key or value silently corrupts character conversion rather than producing an obvious compile-time failure.

Important risks visible in this chunk:

- Binary search requires sorted keys. This chunk is sorted in nondecreasing order, but duplicate key `0xE58D84` can make selected output depend on `kiconv_binsearch()` duplicate handling.
- `KICONV_UTF8_EUCTW_MAX` must remain synchronized with the complete array length across all chunks. This chunk alone has 12,919 rows and does not validate the full count.
- The source comment says some characters are missing and CNS11643-92 is unsupported; callers must tolerate unmappable Unicode input.
- The array is mutable (`static kiconv_table_t`, not `const`), even though it is lookup data. Accidental writes in an including translation unit would affect conversion behavior.
- Since this is a generated table in a header, edits can increase kernel object size in every translation unit that includes it.

## Cross-Chunk References

This is chunk 1 for the file. It opens `kiconv_utf8_euctw[]` but does not close it. The next chunk must continue the same initializer starting at line 13008 with key `0xE6AA86` and should verify continued sortedness, eventual array closure, `_KERNEL`/C++ guard closure, and total entry count against `KICONV_UTF8_EUCTW_MAX`.

The reverse-direction file `kiconv_euctw_utf8.h` is related but separate: it maps CNS/EUC-TW plane tables back to UTF-8 and helps interpret this chunk's packed destination values.

### Chunk 2: lines 13008-25996

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_euctw.h lines 13008-25996

## Scope

This report covers only `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_euctw.h` lines 13008-25996 in learn_fs subset A (`Docs/research_subset_a.md`). I read the requested range completely. Adjacent context was used only to confirm that the range is a middle slice of the same `kiconv_utf8_euctw[]` initializer opened earlier and continued after line 25996.

The chunk is static kernel character-conversion data, not executable conversion logic. It contains no declarations, preprocessor directives, comments, or array boundaries.

## APIs And Exported Data

This chunk contributes 12,989 rows to:

- `static kiconv_table_t kiconv_utf8_euctw[]`

`kiconv_table_t` is the common CCK conversion table type declared in `kiconv_cck_common.h` as two `uint32_t` fields: `key` and `value`. In this table:

- `key` is a packed UTF-8 byte sequence encoded as a hexadecimal integer.
- `value` is a packed CNS 11643/EUC-TW destination code.

No new API, macro, type, or symbol is introduced in this chunk. Runtime users depend on the table-level API and constants declared outside this line range, especially `KICONV_UTF8_EUCTW_MAX`, `kiconv_utf8_euctw[]`, and the shared `kiconv_binsearch()` contract.

## Data Shape

The first and last rows in this chunk are:

- line 13008: `0xE6AA86 -> 0x3D5A1`
- line 25996: `0xF0A09B8D -> 0x6A3E6`

Decoded as Unicode scalar values, this chunk spans from `U+6A86` through `U+206CD`. It covers the later part of the BMP CJK Unified Ideographs block and then enters supplementary-plane CJK data encoded as four-byte UTF-8.

Observed properties for lines 13008-25996:

- 12,989 table rows.
- 11,811 rows use three-byte UTF-8 keys.
- 1,178 rows use four-byte UTF-8 keys.
- No non-table lines.
- No duplicate UTF-8 keys within this chunk.
- Strictly ascending packed UTF-8 key order within this chunk.

Destination value distribution by high CNS/packed plane prefix:

- `0x1....`: 3,322 entries
- `0x2....`: 5,271 entries
- `0x3....`: 2,497 entries
- `0x4....`: 652 entries
- `0x5....`: 283 entries
- `0x6....`: 427 entries
- `0x7....`: 83 entries
- `0xF....`: 454 entries

The observed destination range is `0x1A1A2` through `0xFECC9`, so this slice includes normal CNS plane mappings and `0xF....` private/compatibility-style mappings used by the EUC-TW table.

## Control Flow

There is no direct control flow in this chunk: no functions, branches, loops, locking, allocation, or error handling.

Runtime behavior is indirect:

1. The UTF-8-to-CCK/EUC-TW converter parses and validates a UTF-8 sequence.
2. The sequence is packed into a `uint32_t` key compatible with this table.
3. The converter searches `kiconv_utf8_euctw[]`, normally through the shared binary-search API declared as `kiconv_binsearch(uint32_t key, void *tbl, size_t nitems)`.
4. On success, the packed CNS/EUC-TW value from this chunk is emitted by conversion logic outside this header.
5. On miss, invalid input or unmappable-character handling is performed by the common kiconv wrapper code, not by this table.

Because lookup is binary-search based, sorted key order is a functional invariant. This chunk preserves that invariant internally and across the visible boundaries: line 13007 is `0xE6AA85`, this chunk starts at `0xE6AA86`, this chunk ends at `0xF0A09B8D`, and line 25997 continues with `0xF0A09B8E`.

## State And Dependencies

All state here is compiled static data. The parent array is declared `static` in a kernel header, so including translation units receive internal-linkage copies rather than referencing one external object.

Dependencies visible from the table and adjacent common code:

- `_KERNEL` guard around the parent table outside this chunk.
- `kiconv_table_t` from `sys/kiconv_cck_common.h`.
- `uint32_t` storage for packed source and destination values.
- Common kiconv UTF-8-to-CCK wrappers: `kiconv_utf8_to_cck()` and `kiconvstr_utf8_to_cck()`.
- Common lookup helper: `kiconv_binsearch()`.
- EUC-TW/CNS parsing constants in `sys/kiconv_tc.h`, including `KICONV_TC_EUCTW_MBYTE`, `KICONV_TC_EUCTW_PMASK`, and valid EUC-byte predicates.
- Kernel encoding registration in `uts/common/os/kiconv.c`, where `"euctw"` is a recognized normalized code name.
- Header installation/listing in `uts/common/sys/Makefile`, which includes `kiconv_utf8_euctw.h`.

## Risks And Edge Cases

- Table edits are high risk because an incorrect literal silently changes character conversion output.
- Binary search depends on strict ordering. This chunk is strictly ascending, but future edits must preserve ordering at both chunk boundaries.
- `KICONV_UTF8_EUCTW_MAX` is a file-level count contract. This chunk contributes 12,989 entries but cannot validate the complete table alone.
- The parent table is mutable (`static kiconv_table_t`, not `const`) even though it is intended as lookup data; accidental writes by an including translation unit could corrupt conversion behavior.
- The table's file-level comments state that some characters are missing and CNS11643-92 is not supported, so unmappable input is expected for parts of Unicode outside the historical mapping source.
- Packed destination values are not self-describing in this chunk. Correct byte emission depends on external EUC-TW/CNS interpretation logic using the same plane/value encoding assumptions.
- The chunk includes four-byte UTF-8 keys for supplementary-plane CJK characters. Any consumer that assumes three-byte UTF-8 would mishandle the later part of this range.

## Cross-Chunk References

This is chunk 2 for `kiconv_utf8_euctw.h`. It continues the array opened in the previous chunk:

- Previous visible row: line 13007, `0xE6AA85 -> 0x2DDB4`.
- This chunk starts: line 13008, `0xE6AA86 -> 0x3D5A1`.

The next chunk must continue the same initializer:

- This chunk ends: line 25996, `0xF0A09B8D -> 0x6A3E6`.
- Next visible row: line 25997, `0xF0A09B8E -> 0x4A3C1`.

Later chunks must verify the final array closure, `_KERNEL`/C++/include-guard closure, and complete entry count against `KICONV_UTF8_EUCTW_MAX`. The reverse-direction file `kiconv_euctw_utf8.h` is related but separate; it stores CNS/EUC-TW plane-keyed tables mapping back to UTF-8.

### Chunk 3: lines 25997-37911

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_euctw.h lines 25997-37911

## Scope

This chunk is a contiguous middle slice of the illumos kernel UTF-8-to-EUC-TW mapping header. It sits entirely inside:

- `static kiconv_table_t kiconv_utf8_euctw[] = { ... }`

The range contains 11,915 initializer rows and no executable functions, macros, typedefs, conditionals, or closing braces. Runtime behavior is therefore fully data-driven by common kiconv conversion code that packs validated UTF-8 input into table keys, searches this sorted table, and emits the stored EUC-TW/CNS value.

## APIs And Data Structures

- This chunk contributes rows to `kiconv_utf8_euctw[]`, declared earlier in the file under `_KERNEL`.
- The file-level table count contract is `KICONV_UTF8_EUCTW_MAX (55442)`.
- Each row uses `kiconv_table_t` from `sys/kiconv_cck_common.h`:
  - `uint32_t key`: packed UTF-8 byte sequence.
  - `uint32_t value`: packed EUC-TW destination encoding.
- Visible key range in this chunk:
  - first row: `0xF0A09B8E -> 0x4A3C1`
  - last row: `0xF0A4AD90 -> 0x5BAB4`
- All keys in this range are 4-byte UTF-8 packed values with lead byte `0xF0`, covering supplementary-plane Unicode mappings.

## Control Flow

There is no direct control flow in the chunk. The relevant runtime flow is outside this header:

1. Common UTF-8-to-CCK conversion logic determines the UTF-8 sequence length with `u8_number_of_bytes[]`.
2. It validates continuation bytes and second-byte bounds with `u8_valid_min_2nd_byte[]` and `u8_valid_max_2nd_byte[]`.
3. It packs the UTF-8 bytes into a `uint32_t` key.
4. It binary-searches the selected sorted table.
5. On match, it writes the mapped target bytes; on miss or invalid input, surrounding conversion code handles replacement, `EILSEQ`, `EINVAL`, or `E2BIG`.

The chunk’s sort order is part of that binary-search contract. A read-only check over the line range found no descending keys and no duplicate keys inside the chunk.

## State

The chunk is immutable static initializer data. It does not allocate memory, mutate state, perform locking, or maintain per-conversion state. Conversion state such as BOM handling, buffer pointers, non-identical conversion counts, null handling, and replacement policy lives in the kiconv driver code rather than in this header.

## Data Shape

- Rows in this chunk: 11,915.
- Key ordering: ascending, unique within the chunk.
- Key gaps: expected; the table only includes mapped Unicode scalar values.
- Destination value range seen in this chunk: `0x3A3D9` through `0xFEDB4`.
- Destination value high-nibble/plane distribution visible in this chunk:
  - `0x3....`: 14 rows
  - `0x4....`: 1,216 rows
  - `0x5....`: 2,832 rows
  - `0x6....`: 3,031 rows
  - `0x7....`: 1,684 rows
  - `0xF....`: 3,138 rows
- The `0xF....` destination values correspond to EUC-TW/private-use/UDA-style encoded values, consistent with `kiconv_tc.h` documenting EUC-TW planes 12/13/14/16 in the Unicode private-use range.

## Dependencies

- `_KERNEL` guard and `_SYS_KICONV_UTF8_EUCTW_H` include guard declared outside this chunk.
- `kiconv_table_t` from `sys/kiconv_cck_common.h`.
- UTF-8 validation tables declared in `sys/kiconv_cck_common.h` and provided by common Unicode textprep code.
- Traditional Chinese/EUC-TW constants in `sys/kiconv_tc.h`, including `KICONV_TC_EUCTW_MBYTE`, `KICONV_TC_EUCTW_PMASK`, and UDA range constants.
- The reverse-direction mapping is in `sys/kiconv_euctw_utf8.h`.
- `usr/src/uts/common/sys/Makefile` exports `kiconv_utf8_euctw.h` as an illumos kernel/system header.

## Risks And Cross-Chunk References

- Count drift risk: changes to this data must keep the full-file `KICONV_UTF8_EUCTW_MAX` aligned with the complete initializer length.
- Sort-order risk: common conversion code relies on sorted keys for binary search. Insertions must preserve ascending key order across chunk boundaries.
- Boundary continuity:
  - The previous chunk ends before this range at `0xF0A09B8D -> 0x6A3E6`; this chunk continues at `0xF0A09B8E`.
  - The next chunk should continue after this range at `0xF0A4AD91 -> 0x5BAB3`.
- Generated-data risk: this file appears to be a generated Unicode/CNS mapping table. Manual edits can introduce asymmetric mappings with `kiconv_euctw_utf8.h`, wrong EUC-TW plane encodings, or missing supplementary-plane entries.
- Error-handling risk is external: this table has no invalid-entry sentinel in the chunk, so unmapped input depends on the caller’s search-miss and replacement policy.

### Chunk 4: lines 37912-49826

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_euctw.h lines 37912-49826

This chunk is part of learn_fs subset A because `sources/os/illumos/illumos-gate` is in `Docs/research_subset_a.md`. I read the full requested range, lines 37912-49826, and used adjacent context only to identify the enclosing table declaration, shared table type, and neighboring table boundaries.

The source file is a generated-style illumos kernel iconv mapping header for UTF-8 to EUC-TW/CNS 11643 conversion. This chunk contains only initializer rows inside `static kiconv_table_t kiconv_utf8_euctw[]`; it has no function definitions, local branches, loops, calls, allocation, locking, or direct filesystem/block-storage behavior.

## APIs and Data Surface

- Enclosing declaration: `static kiconv_table_t kiconv_utf8_euctw[]`, opened at line 88 under `_KERNEL`.
- Count contract: `KICONV_UTF8_EUCTW_MAX (55442)`, defined before the array and applying to the complete table, not this chunk alone.
- Entry type: `kiconv_table_t` from `sys/kiconv_cck_common.h`, with `uint32_t key` and `uint32_t value`.
- This chunk contributes 11,915 complete rows.
- First row in this chunk: `0xF0A4AD91 -> 0x5BAB3`.
- Last row in this chunk: `0xF0A8AB8B -> 0xFE1B9`.

Every key in this slice is an encoded four-byte UTF-8 value beginning with `0xF0`, so the chunk covers supplementary-plane Unicode code points represented in the table's packed-UTF-8 key format. Values are packed CNS/EUC-TW destinations. In this slice, destination prefixes distribute as: prefix `0x3` has 4 rows, `0x4` has 1,446 rows, `0x5` has 3,356 rows, `0x6` has 2,147 rows, `0x7` has 2,702 rows, and `0xF` has 2,260 rows.

## Control Flow and Runtime Use

There is no executable control flow in the chunk. Runtime behavior is indirect:

1. Common UTF-8-to-CCK conversion code accumulates an input UTF-8 scalar into the packed integer key format.
2. The EUC-TW converter searches `kiconv_utf8_euctw[]`, using the sorted key table contract exposed by `kiconv_binsearch(uint32_t key, void *tbl, size_t nitems)`.
3. On a hit, the 32-bit `value` is decoded by conversion code outside this chunk into the output EUC-TW/CNS bytes.
4. Buffer accounting, invalid-sequence handling, replacement behavior, and errno propagation live in shared kiconv code, not in this table slice.

The key column in this chunk is strictly ascending, with no duplicate keys detected in the requested range.

## State and Dependencies

The chunk defines static header data only. It introduces no mutable runtime state beyond the `static` array object created in each translation unit that includes the header. It performs no synchronization and has no lifecycle hooks.

Direct dependencies visible from adjacent context:

- `_KERNEL` guard and `_SYS_KICONV_UTF8_EUCTW_H` include guard.
- `kiconv_table_t`, `uint32_t`, and common UTF-8-to-CCK conversion prototypes from `sys/kiconv_cck_common.h`.
- EUC-TW byte-shape and plane constants from `sys/kiconv_tc.h`, including `KICONV_TC_EUCTW_MBYTE` and `KICONV_TC_EUCTW_PMASK`.
- Registration context in `uts/common/os/kiconv.c`, where encoding name `"euctw"` is mapped to code id `16`.
- Export context in `uts/common/sys/Makefile`, which lists `kiconv_utf8_euctw.h` as an installed/exported sys header.
- Reverse-direction consistency with `sys/kiconv_euctw_utf8.h`, which has per-plane `kiconv_cnsN_utf8[]` tables.

## Risks and Maintenance Notes

- Table ordering is part of the functional contract. Reordering or inserting rows incorrectly can break binary-search lookup even though the C syntax still compiles.
- `KICONV_UTF8_EUCTW_MAX` must remain aligned with the complete table length.
- The header comment says the data supports Unicode 3.2 / `Unihan-3.2.0.txt`, includes plane 1/2/14 mappings, and supports CNS11643-86 but not CNS11643-92.
- The table is not declared `const`; accidental writes by including code would mutate conversion behavior for that translation unit.
- Round-trip behavior depends on consistency with `kiconv_euctw_utf8.h`.
- The `0x0000 -> 0x0003F` special non-identical-conversion entry is outside this chunk.

## Cross-Chunk References

- Previous chunk(s) provide the file prologue, guards, `KICONV_UTF8_EUCTW_MAX`, the `kiconv_utf8_euctw[]` declaration, the non-identical-conversion sentinel, and all rows before key `0xF0A4AD91`.
- This chunk continues the same single `kiconv_utf8_euctw[]` table from `0xF0A4AD91` through `0xF0A8AB8B`; it does not open or close any declarations.
- Later chunk(s) must continue the same table after line 49826, eventually closing the array near the end of the file and then closing the `_KERNEL`, C++, and include guards.

### Chunk 5: lines 49827-55539

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_euctw.h lines 49827-55539

## Scope

This chunk is the final slice of the kernel-only `kiconv_utf8_euctw[]` mapping table. The table is declared earlier as `static kiconv_table_t kiconv_utf8_euctw[]` and maps UTF-8 byte sequences, encoded as packed `uint32_t` keys, to packed EUC-TW/CNS 11643 output values. The file comment says the table covers UTF-8 to CNS 11643, includes planes 1/2/14, supports CNS11643-86, and is based on Unicode 3.2 / Unihan 3.2.0.

## APIs And Data

- Public symbols visible from this chunk: none newly declared. The chunk completes an existing static array and closes `_KERNEL`, `extern "C"`, and `_SYS_KICONV_UTF8_EUCTW_H` guards.
- Main data contribution: 5,704 `kiconv_table_t` initializer entries from `0xF0A8AB8C -> 0xFE1B5` through `0xF0AFA89D -> 0x7DECD`.
- Table element type comes from `kiconv_cck_common.h`: `kiconv_table_t` has `uint32_t key` and `uint32_t value`.
- The enclosing file defines `KICONV_UTF8_EUCTW_MAX` as `55442`; consumers must use the whole-table count, not this chunk count.

## Control Flow

There is no executable control flow in the chunk. Runtime behavior is indirect: the common UTF-8-to-CCK conversion path can binary-search sorted `kiconv_table_t` arrays and emit the mapped value when a key is found.

## State And Dependencies

- State is compile-time static mapping data under `#ifdef _KERNEL`; no mutable state is introduced.
- The chunk depends on earlier file context for the array declaration, header guard, and table metadata.
- It depends structurally on `kiconv_table_t` and common kiconv conversion helpers declared in `sys/kiconv_cck_common.h`.
- The file is listed by `usr/src/uts/common/sys/Makefile`.

## Risks

- Ordering is critical because the common lookup path expects sorted UTF-8 keys for binary search.
- Count consistency is critical: `KICONV_UTF8_EUCTW_MAX` must match the full array entry count.
- The table is old by design: Unicode 3.2 / Unihan 3.2.0, with CNS11643-92 not supported.
- Raw initializer transcription errors can compile cleanly while producing incorrect character conversion.

## Cross-Chunk References

- Earlier chunks define the header metadata, `KICONV_UTF8_EUCTW_MAX`, the array declaration, the special non-identical conversion entry, and preceding mappings.
- Chunk 4 directly precedes this range and ends at `0xF0A8AB8B -> 0xFE1B9`; this chunk starts at `0xF0A8AB8C -> 0xFE1B5`.
- This is the terminal chunk for the file; it supplies the final entries and closing syntax for the array and guards.

## Verification

- Read `Docs/research_subset_a.md` and confirmed `sources/os/illumos/illumos-gate` is in subset A.
- Read the complete requested range, lines 49827-55539.
- Checked adjacent context around the declaration and closeout.
- Wrote the chunk report to `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_utf8_euctw_70711169f840_research.md`.
- Did not create the final per-file merged report.
