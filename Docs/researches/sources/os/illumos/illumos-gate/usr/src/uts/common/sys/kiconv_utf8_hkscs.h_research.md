# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_hkscs.h

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-13702, source bytes 262137, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_utf8_hkscs_6b547d3444a2_research.md`
- chunk 2: lines 13703-18512, source bytes 94697, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_utf8_hkscs_ae2d2eb59a09_research.md`

## Chunk Research

### Chunk 1: lines 1-13702

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_hkscs.h lines 1-13702

## Scope

This chunk is the first 13,702 lines of the illumos kernel UTF-8 to BIG5-HKSCS(2004) conversion table header. It is in scope because `Docs/research_subset_a.md` includes `sources/os/illumos/illumos-gate`.

The full file has 18,512 lines and 18,420 mapping entries. This chunk contains the license block, header guards, kernel-only declaration area, table-count macro, and the first 13,619 entries of `kiconv_utf8_hkscs[]`. The array remains open at the end of this chunk.

## Public Surface In This Chunk

- Header guard: `_SYS_KICONV_UTF8_HKSCS_H`.
- C++ linkage wrapper: `extern "C"` around the kernel declarations.
- Kernel-only guard: all exported content is under `#ifdef _KERNEL`.
- Full-file mapping count macro: `KICONV_UTF8_HKSCS_MAX` is `18420`.
- Static table: `static kiconv_table_t kiconv_utf8_hkscs[] = { ... }` starts at line 81.

This header does not define functions or new types. It depends on including context for `kiconv_table_t` and `uint32_t`.

## Data Shape And Invariants

Each normal row maps one packed UTF-8 byte sequence integer to one packed BIG5-HKSCS code value. For example, line 82 maps `0x0000` to ASCII replacement `0x003f`, and the chunk ends at line 13702 with `0xE8BA97 -> 0xf763`.

Observed across lines 82-13702:

- Mapping rows in this chunk: 13,619.
- Full-file rows declared by macro: 18,420.
- UTF-8 key range in this chunk: `0x0000` through `0xE8BA97`.
- Duplicate UTF-8 keys: 0.
- Descending key transitions: 0.
- Special non-code values: 2.
- Value range for ordinary numeric targets: `0x003f` through `0xfefe`.
- Ordinary two-byte target rows: 13,616, plus the initial `0x003f` fallback row.

The visible key distribution is one ASCII/fallback row, Latin/Greek/Cyrillic rows in `0xC2` through `0xD1`, four `0xE1` rows, then large BMP blocks: `0xE2` has 206 rows, `0xE3` has 586, `0xE4` has 606, `0xE5` has 3,035, `0xE6` has 3,155, `0xE7` has 3,062, and this chunk's partial `0xE8` block has 2,783.

## Special Rows

Two entries do not map directly to a BIG5-HKSCS code value:

- Line 96: `0xC38A` uses `(uint32_t)-1`.
- Line 105: `0xC3AA` uses `(uint32_t)-2`.

The adjacent comments identify these as Unicode `0x00ca` and `0x00ea` cases with multiple possible sequences involving combining marks. `kiconv_cck_common.h` declares `kiconv_utf8tocck_t` with `ib` and `ibtail` parameters noted as currently used by BIG5HKSCS only, so these negative values are table-level sentinels for conversion logic that must inspect surrounding input rather than blindly emit the table value.

## Dependencies

- `usr/src/uts/common/sys/kiconv_cck_common.h` defines `kiconv_table_t` as `{ uint32_t key; uint32_t value; }`, declares `kiconv_binsearch()`, and declares common UTF-8-to-CCK wrappers.
- `usr/src/uts/common/sys/kiconv.h` defines the kernel kiconv framework, conversion operation tables, descriptor state, replacement characters, and module IDs.
- `usr/src/uts/common/os/kiconv.c` lists normalized code names including `"big5hkscs"` with code ID `15` and `"cp950hkscs"` with code ID `17`.
- `usr/src/uts/common/sys/kiconv_hkscs_utf8.h` is the sibling reverse-direction BIG5-HKSCS to UTF-8 table.
- `usr/src/uts/common/sys/kiconv_utf8_cp950hkscs.h` is the nearby Windows-compatible CP950HKSCS forward table.
- `usr/src/uts/common/sys/Makefile` includes `kiconv_utf8_hkscs.h` in the sys header list.

Direct references to `kiconv_utf8_hkscs` by symbol name were not found outside this header in the visible tree. The visible contract is the static table, the count macro, and the common CCK conversion API declarations.

## Control Flow Impact

This chunk has no executable control flow. Its impact is lookup data for the kernel kiconv Traditional Chinese conversion path:

1. Kernel kiconv normalizes and resolves a conversion involving `"big5hkscs"`.
2. The Traditional Chinese conversion module includes the appropriate generated table.
3. UTF-8 input bytes are validated and packed into an integer key.
4. The key is searched in a sorted `kiconv_table_t` array.
5. The mapped BIG5-HKSCS value is emitted, or special/failure handling is applied by the caller.

The sorted, duplicate-free invariant is essential because the common CCK API exposes binary-search based lookup support.

## State

This chunk declares no mutable runtime state. The table has internal linkage because it is `static`; each translation unit that includes the header can receive its own table copy. The data is effectively compile-time read-only, but it is not declared `const`.

Runtime state, buffer pointers, conversion descriptors, error reporting, and replacement policy live in the kiconv framework and common CCK conversion wrappers, not in this header.

## Risks And Cross-Chunk References

- This chunk ends mid-initializer after `0xE8BA97, 0xf763,`; the next visible row is `0xE8BA98, 0xf846,`.
- The remaining 4,801 entries, closing brace, and closing conditional guards are outside this chunk.
- `KICONV_UTF8_HKSCS_MAX` is the full-file count, not the count of this chunk.
- Any inserted, removed, duplicated, or out-of-order row can break binary-search lookup behavior or desynchronize the macro count.
- The `(uint32_t)-1` and `(uint32_t)-2` sentinel rows are correctness-sensitive; generic emitters that treat them as normal code values would corrupt output.
- Forward mappings should stay consistent with `kiconv_hkscs_utf8.h`, but HKSCS compatibility cases and composition-sensitive rows may not be trivially one-to-one.
- Because this is a large `static` table in a header, accidental broad inclusion can duplicate kernel text/data footprint.
- No final per-file report was created for this chunked file.

### Chunk 2: lines 13703-18512

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_hkscs.h lines 13703-18512

## Scope

This chunk covers lines 13703-18512 of `kiconv_utf8_hkscs.h` for `learn_fs` subset A. It is the final ordered segment of the kernel UTF-8-to-BIG5-HKSCS(2004) mapping table. The range starts mid-initializer at UTF-8 key `0xE8BA98`, continues through the end of the mapping data, and includes the closing table brace plus `_KERNEL`, C++ wrapper, and header-guard closures.

This chunk is data-only. It does not create the final per-file report.

## Public Surface And APIs

No new callable APIs, typedefs, or exported functions are introduced in this range. The chunk contributes rows to the file-level static table declared earlier:

- Header guard: `_SYS_KICONV_UTF8_HKSCS_H`.
- Kernel gate: table data is only compiled under `_KERNEL`.
- Macro declared earlier: `KICONV_UTF8_HKSCS_MAX (18420)`.
- Data object declared earlier: `static kiconv_table_t kiconv_utf8_hkscs[]`.
- Table element contract from `kiconv_cck_common.h`: `uint32_t key` and `uint32_t value`.

Each row stores a UTF-8 byte sequence packed as a hexadecimal integer key and a destination BIG5-HKSCS code value in the low 16 bits of `value`.

## Chunk Contents

The chunk contains 4,801 mapping rows:

- First row in chunk: `0xE8BA98 -> 0xf846`.
- Last row in chunk: `0xF0AFA794 -> 0x8ff0`.
- Key ordering in this chunk is ascending with no duplicate keys found by a local scan.
- Key sizes visible in this chunk: 3,108 three-byte UTF-8 keys and 1,693 four-byte UTF-8 keys.
- The table initializer closes at line 18504, followed by `_KERNEL`, `extern "C"`, and `_SYS_KICONV_UTF8_HKSCS_H` closeout lines.

## Control Flow

There is no executable control flow in this chunk. Runtime behavior is controlled by kernel kiconv code that includes this header, packs UTF-8 input bytes into a `uint32_t` key, searches `kiconv_utf8_hkscs[]`, and emits the mapped HKSCS value.

## State And Dependencies

State in this range is static initializer data. It is not declared `const`, but consumers should treat it as immutable conversion metadata.

Dependencies include `_KERNEL`, `kiconv_table_t`, the sorted-table search contract, and sibling kiconv tables such as `kiconv_hkscs_utf8.h`, `kiconv_utf8_cp950hkscs.h`, and `kiconv_cp950hkscs_utf8.h`.

## Risks And Cross-Chunk References

- Earlier chunk(s) contain the license, macro, table declaration, sentinel/default row, and mappings before `0xE8BA98`.
- Full-file merge should reconcile row count against `KICONV_UTF8_HKSCS_MAX`; a simple local pair-line count sees 18,418 rows while the macro says 18,420.
- Consumers likely rely on ascending keys for binary search.
- The large `static` header table can duplicate storage across translation units.
- `0xF0...` keys are packed UTF-8 bytes, not Unicode scalar values.
