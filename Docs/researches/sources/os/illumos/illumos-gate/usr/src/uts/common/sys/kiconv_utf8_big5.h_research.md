# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_big5.h

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-13699, source bytes 262141, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_utf8_big5__20577447e3db_research.md`
- chunk 2: lines 13700-13801, source bytes 1858, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_utf8_big5__3ae87638a735_research.md`

## Chunk Research

### Chunk 1: lines 1-13699

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_big5.h lines 1-13699

## Scope

- Repository subset: `Docs/research_subset_a.md`; `sources/os/illumos/illumos-gate` is explicitly in scope.
- Source span read completely: lines 1-13699 of `usr/src/uts/common/sys/kiconv_utf8_big5.h`.
- This is chunk 1 of an oversized kernel header. It covers the license block, include/C++/kernel guards, `KICONV_UTF8_BIG5_MAX`, and the first 13,618 entries of the `kiconv_utf8_big5[]` UTF-8 to BIG5 mapping table.
- The chunk ends inside the table at line 13699; it does not include the final table entries, closing `};`, or closing preprocessor guards.

## APIs and Data Structures

- The header is protected by `_SYS_KICONV_UTF8_BIG5_H` and exposes content only under `_KERNEL`.
- `KICONV_UTF8_BIG5_MAX` is defined as `13711`, matching the full table row count observed in adjacent context.
- The only declared symbol in this chunk is `static kiconv_table_t kiconv_utf8_big5[]`.
- `kiconv_table_t` comes from `usr/src/uts/common/sys/kiconv_cck_common.h` and is:
  - `uint32_t key`
  - `uint32_t value`
- In this table, `key` is a packed UTF-8 byte sequence and `value` is a packed BIG5 two-byte code, except the first sentinel row.

## Mapping Content

- Chunk row count: 13,618 mapping rows.
- First row: `0x0000 -> 0x003f`, documented as the special hold entry for non-identical conversion.
- First real mapping: `0xC2A2 -> 0xa246`.
- Last row in this chunk: `0xEFB9A4 -> 0xa1e0`.
- Sample checkpoints:
  - Row 100, line 181: `0xD0BD -> 0xc7d6`
  - Row 1,000, line 1081: `0xE584A5 -> 0xecba`
  - Row 5,000, line 5081: `0xE6A78C -> 0xba6c`
  - Row 10,000, line 10081: `0xE89E9E -> 0xbfc2`
- Key distribution in this chunk is dominated by three-byte UTF-8:
  - 1 sentinel/ASCII-range key
  - 118 two-byte UTF-8 packed keys
  - 13,499 three-byte UTF-8 packed keys
  - 13,068 keys in the CJK Unified Ideographs UTF-8 byte range
- Value validation over this chunk found one sentinel value and no malformed BIG5 byte pairs by the visible BIG5 byte rules: high byte `0x81..0xfe`; low byte `0x40..0x7e` or `0xa1..0xfe`.

## Control Flow

- There is no executable control flow in this chunk. It is compile-time data consumed by conversion code.
- The sorted ascending `key` order is the important behavioral property: common conversion code and CCK wrappers use binary-search-style lookup over mapping tables.
- Mechanical checks over lines 1-13699 found:
  - no non-ascending keys
  - no duplicate keys
  - no invalid BIG5 byte pairs among non-sentinel values

## State and Dependencies

- State is static kernel data emitted into each translation unit that includes this header because the table is declared `static` in a header.
- Direct visible dependencies:
  - `_KERNEL` guard
  - `kiconv_table_t` from `kiconv_cck_common.h`
  - kernel integer typedefs such as `uint32_t`
- `usr/src/uts/common/sys/Makefile` lists `kiconv_utf8_big5.h` in the common sys header set.
- A direct reference search under `usr/src` found only this header and the sys header makefile entry for `kiconv_utf8_big5`; no direct include or consumer symbol reference was visible in the checked tree.

## Risks

- Data integrity is the main risk. A single wrong literal silently corrupts UTF-8 to BIG5 conversion for that character.
- `KICONV_UTF8_BIG5_MAX` must remain synchronized with the full table length. The full file has 13,711 table rows; this chunk owns 13,618 of them.
- Binary search requires the packed UTF-8 keys to stay strictly ascending. Insertions or regeneration must preserve ordering.
- The initial `0x0000 -> 0x003f` sentinel is not a normal BIG5 mapping and should not be removed or counted as a Unicode character mapping without checking the converter logic.
- Because this is a `static` table in a header, broad inclusion can duplicate the table in multiple objects; this is an established pattern in these kiconv generated headers but has code-size implications.

## Cross-Chunk References

- The next chunk/tail starts at line 13700 with `0xEFB9A5 -> 0xa1e1`.
- Adjacent context shows 93 remaining rows after this chunk, ending at `0xEFBDA4 -> 0xa14e`, followed by the table close and `_KERNEL`, C++, and header guard closures.
- Any final per-file merge should combine this chunk with the tail so the report can state the full `KICONV_UTF8_BIG5_MAX == 13711` invariant and final closure ownership.
- No final per-file report was created.

### Chunk 2: lines 13700-13801

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_big5.h lines 13700-13801

## Scope

This report covers lines 13700-13801 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_big5.h` for `learn_fs` subset A. The chunk is the final ordered segment of the kernel UTF-8-to-Big5 mapping table. It begins at the row for UTF-8 byte sequence `0xEFB9A5` and reaches EOF, including the closing table initializer and preprocessor guard closures.

## Public Surface And APIs

This chunk does not introduce new callable APIs, macros, typedefs, or exported symbols. It contributes data to the file-level static kernel table declared earlier as:

- `#define KICONV_UTF8_BIG5_MAX (13711)`
- `static kiconv_table_t kiconv_utf8_big5[] = { ... }`

The table element type is `kiconv_table_t` from `kiconv_cck_common.h`, with two `uint32_t` fields:

- `key`: UTF-8 bytes packed into a scalar table key.
- `value`: destination Big5 code unit stored as a 16-bit value inside the 32-bit field.

## Control Flow

There is no executable control flow in this chunk. Runtime behavior is data-driven in kernel iconv code that includes this header: UTF-8 input is packed into a key, `kiconv_utf8_big5[]` is searched, and the matching Big5 value is emitted. Invalid, unmapped, or replacement behavior is handled outside this data header.

## State And Dependencies

All state in this range is immutable static initializer data compiled only under `_KERNEL`. The chunk contains 93 mapping rows, from `0xEFB9A5 -> 0xa1e1` through `0xEFBDA4 -> 0xa14e`, then closes:

- `kiconv_utf8_big5[]` at line 13793
- `_KERNEL` at line 13795
- C++ wrapper at lines 13797-13799
- `_SYS_KICONV_UTF8_BIG5_H` at line 13801

Dependencies include `_KERNEL`, `_SYS_KICONV_UTF8_BIG5_H`, `kiconv_table_t`, `uint32_t`, and external kiconv conversion logic.

## Risks And Cross-Chunk References

The chunk’s main risks are generated-data drift, table count mismatch with `KICONV_UTF8_BIG5_MAX`, and preserving sorted key order. The visible mappings remain ascending despite intentional gaps such as `0xEFBC81 -> 0xEFBC83`.

Earlier chunk(s) contain the license, include guard, macro definition, table declaration, special hold entry `0x0000 -> 0x003f`, and preceding mappings through `0xEFB9A4 -> 0xa1e0`. This chunk supplies the final 93 rows and file closure; the per-file merge should verify full initializer length, ascending keys, and the final guard order.
