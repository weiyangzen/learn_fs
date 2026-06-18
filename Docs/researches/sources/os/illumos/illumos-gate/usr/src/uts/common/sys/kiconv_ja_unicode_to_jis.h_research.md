# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_ja_unicode_to_jis.h

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-7089, source bytes 262116, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_ja_unicode_c0be363ae220_research.md`
- chunk 2: lines 7090-7616, source bytes 21661, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_ja_unicode_6fb396351a07_research.md`

## Chunk Research

### Chunk 1: lines 1-7089

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_ja_unicode_to_jis.h lines 1-7089

## Scope

This chunk covers the opening 7,089 lines of `kiconv_ja_unicode_to_jis.h`, an illumos kernel-only Japanese Unicode-to-JIS/EUC lookup header. It includes the license/header guard, kernel gating, dependencies, the `NODEST` alias, and nearly all `static const kiconv_ja_euc16_t` UCS-2 high-byte lookup blocks from block `00` through the beginning of block `E7`.

The chunk ends inside `kiconv_ja_ucs2_to_euc16_block_E7`; the final entries of that block, the high-byte block index, the EUC-JP-MS/CP932 compatibility macro, `#undef NODEST`, and closing preprocessor guards are outside this chunk.

## APIs And Exports

- Header identity: `_SYS_KICONV_JA_UNICODE_TO_JIS_H`.
- C++ compatibility: wraps declarations in `extern "C"` when compiled as C++.
- Dependencies:
  - `<sys/kiconv.h>` for the broader kernel iconv interfaces.
  - `<sys/kiconv_ja.h>` for Japanese conversion constants and typedefs, especially `KICONV_JA_NODEST` and `kiconv_ja_euc16_t`.
- Kernel-only scope: all conversion data in this chunk is inside `#ifdef _KERNEL`, so userland inclusion sees only the guard/C++ wrapper shell.
- Local macro:
  - `NODEST` is defined as `KICONV_JA_NODEST`, whose definition in adjacent dependency context is `0xffff`.
- Static data exports within the translation unit that includes this header:
  - `kiconv_ja_ucs2_to_euc16_block_00`
  - `kiconv_ja_ucs2_to_euc16_block_01`
  - `kiconv_ja_ucs2_to_euc16_block_02`
  - `kiconv_ja_ucs2_to_euc16_block_03`
  - `kiconv_ja_ucs2_to_euc16_block_04`
  - `kiconv_ja_ucs2_to_euc16_block_20` through `kiconv_ja_ucs2_to_euc16_block_26`
  - `kiconv_ja_ucs2_to_euc16_block_30`, `32`, `33`
  - `kiconv_ja_ucs2_to_euc16_block_4E` through `9F`
  - `kiconv_ja_ucs2_to_euc16_block_E0` through `E6`
  - the start of `kiconv_ja_ucs2_to_euc16_block_E7`

These arrays are `static const`, so they have internal linkage in each including kernel object and are immutable lookup data rather than callable APIs.

## Data Model

Each block is a 256-entry table indexed by the low byte of a UCS-2 code point. The block suffix is the high byte. For example, a caller using block `4E` maps code points `U+4E00` through `U+4EFF`; array element `0x00` corresponds to `U+4E00`, element `0xFF` to `U+4EFF`.

Values are `kiconv_ja_euc16_t` 16-bit EUC/JIS-family destination codes. `NODEST` marks code points with no destination mapping. Non-`NODEST` entries include ASCII pass-through values, JIS X 0208/EUC-JP-style two-byte values such as `0xa1a1`, IBM/NEC extension ranges such as `0xada1` and `0xf5a1`, and dense private-use mappings.

## Block Coverage In This Chunk

Complete 256-entry blocks in this chunk:

- `00`-`04`: Latin-1/control/Latin Extended/Greek/Cyrillic-related mappings, with ASCII `U+0000`-`U+007F` passed through in block `00`.
- `20`-`26`: punctuation, symbols, arrows/math/box-drawing-like symbol ranges, mostly sparse with many `NODEST` entries.
- `30`, `32`, `33`: CJK symbols and compatibility-like ranges; block `30` contains many common Japanese punctuation/kana/symbol mappings.
- `4E`-`9F`: the main CJK Unified Ideographs area. These blocks contain the bulk of the table and map many Unicode Han code points to JIS/EUC rows, while unsupported ideographs remain `NODEST`.
- `E0`-`E6`: dense private-use area mappings. Blocks `E0` through `E6` have no `NODEST` entries in this chunk and map sequentially through extension codes roughly spanning `0xf5a1` to `0xfe26`.

Partial block:

- `E7`: starts at line 7058. The chunk includes entries `00` through the comment for offset `78`, with mapped values through `0xfe7e` followed by `NODEST` entries. The block continues in the next chunk.

Selected table density observations from the fully read range:

- Sparse symbol blocks include `23` with only one non-`NODEST` entry and `02` with six.
- Dense CJK blocks vary substantially; examples include block `5F` with 193 mapped entries and block `8B` with 99 mapped entries.
- Private-use blocks `E0`-`E6` are fully mapped, suggesting a compact extension encoding area rather than ordinary Unicode coverage.

## Control Flow

There is no executable function body in this chunk. Runtime control flow is implied by table lookup:

1. A Unicode/UCS-2 code point is split into high byte and low byte.
2. The high byte selects a block pointer from the index table defined after this chunk.
3. The low byte indexes the selected 256-entry block.
4. The returned `kiconv_ja_euc16_t` is either a destination EUC/JIS-family code or `KICONV_JA_NODEST`.
5. A caller must treat `NODEST` as an unmappable character and follow the surrounding kiconv error/replacement policy.

The chunk itself provides only the per-block data used by that lookup path.

## State And Mutability

- All conversion tables here are `static const`; they are read-only conversion state with no mutation or synchronization requirements.
- There is no dynamic allocation, reference counting, locking, or per-conversion state in this chunk.
- State correctness depends on positional invariants: every complete block must contain exactly 256 values, and each value's array position is the low-byte mapping for its Unicode code point.

## Dependencies And Integration

- Depends on `kiconv_ja.h` for `KICONV_JA_NODEST`, table ID constants used later in the file, and `kiconv_ja_euc16_t` (`ushort_t`).
- The reverse-direction sibling header `kiconv_ja_jis_to_unicode.h` contains JIS-to-Unicode tables and MS-extension compatibility macros. This file is the Unicode-to-JIS/EUC counterpart.
- `usr/src/uts/common/sys/Makefile` lists this header for installation/export as a kernel system header.
- A repository-wide search found no direct in-tree textual use of the later `kiconv_ja_ucs2_to_euc16_index` or `KICONV_JA_CNV_U2_TO_EUCJPMS` names outside this header, implying consumers may be generated, platform-specific, or outside the searched focus, or the header may be installed for external kernel module consumers.

## Risks And Edge Cases

- Table alignment risk: a missing, extra, or reordered initializer silently maps many Unicode code points incorrectly. The comments every eight entries help humans, but C does not enforce the intended 256-entry size because the arrays use unsized `[]`.
- Sentinel collision risk: `NODEST` is `0xffff`; conversion code must never treat it as a valid destination code.
- Header inclusion cost: because arrays are `static const` in a header, every including translation unit gets its own internal copy unless compiler/linker merging applies.
- Conditional compilation risk: conversion data is unavailable unless `_KERNEL` is defined. Non-kernel consumers including this header will not see the tables.
- Generated-data maintenance risk: values encode standards and vendor compatibility behavior. Manual edits are high-risk without round-trip tests against Unicode/JIS/EUC-JP-MS/CP932 reference data.
- Partial-chunk risk: this chunk cannot validate the final `E7` block length or the index's correspondence to the blocks because both complete in the next chunk.

## Cross-Chunk References

- Next chunk must finish `kiconv_ja_ucs2_to_euc16_block_E7`, then cover blocks `F9`, `FA`, and `FF`.
- Next chunk must cover `kiconv_ja_ucs2_to_euc16_index[]`, which binds high-byte values to these block arrays and places `NULL` for eliminated/unmapped high-byte ranges.
- Next chunk must cover `KICONV_JA_CNV_U2_TO_EUCJPMS(id, e, u)`, the compatibility override macro for EUC-JP-MS and CP932 mappings such as `U+FF5E`, `U+2225`, `U+FF0D`, and currency/fullwidth symbol variants.
- Merge should verify that every complete block from this chunk appears in the index exactly at its high-byte slot and that eliminated high-byte blocks are represented by `NULL`.

### Chunk 2: lines 7090-7616

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_ja_unicode_to_jis.h lines 7090-7616

## Scope

This chunk is the final chunk of the kernel-only Japanese Unicode-to-JIS/EUC conversion header. It covers the end of `kiconv_ja_ucs2_to_euc16_block_E7`, all high-byte blocks `F9`, `FA`, and `FF`, the top-level UCS-2 high-byte index table, the EUC-JP-MS/CP932 Unicode override macro, and the header epilogue.

## APIs and Data Exposed

- `kiconv_ja_ucs2_to_euc16_block_F9[]`: static `kiconv_ja_euc16_t` lookup block for Unicode code points `U+F900..U+F9FF`. Almost every entry is `NODEST`; only `U+F929 -> 0xf445` and `U+F9DC -> 0xf472` are mapped.
- `kiconv_ja_ucs2_to_euc16_block_FA[]`: static lookup block for `U+FA00..U+FAFF`. The mapped span is concentrated in compatibility ideographs `U+FA0E..U+FA2D`, producing destination values `0xf434` through `0xf47d` with gaps; the rest of the block is `NODEST`.
- `kiconv_ja_ucs2_to_euc16_block_FF[]`: static lookup block for `U+FF00..U+FFFF`. It maps fullwidth punctuation/digits/Latin letters, halfwidth Katakana-like values `U+FF61..U+FF9F` to `0x00a1..0x00df`, and a few currency/symbol forms near `U+FFE3`/`U+FFE5`.
- `kiconv_ja_ucs2_to_euc16_index[]`: static pointer index from UCS-2 high byte to a 256-entry block. Present blocks point to arrays defined earlier in this header; absent blocks are explicit `NULL` entries.
- `KICONV_JA_CNV_U2_TO_EUCJPMS(id, e, u)`: macro that initializes `e` to `KICONV_JA_NODEST`, then applies EUC-JP-MS/CP932-only remaps for eight selected Unicode values.

## Control Flow

There are no functions in this chunk. Runtime behavior is table selection plus macro expansion: callers split UCS-2 into high/low bytes, index `kiconv_ja_ucs2_to_euc16_index[]`, check for `NULL`, then index the selected block by low byte. `NODEST` means unmapped.

The override macro only assigns a destination when `id` is `KICONV_JA_TBLID_EUCJP_MS` or `KICONV_JA_TBLID_CP932`; otherwise it leaves `e` as unmapped.

## State and Dependencies

All arrays are `static const`, with no mutable state. The chunk depends on `sys/kiconv_ja.h` for `kiconv_ja_euc16_t`, `KICONV_JA_NODEST`, `KICONV_JA_TBLID_EUCJP_MS`, and `KICONV_JA_TBLID_CP932`. The local `NODEST` alias is undefined at the end. The table body is guarded by `_KERNEL`.

## Risks and Edge Cases

- Consumers must check `NULL` index entries before second-level lookup.
- `KICONV_JA_NODEST` is `0xffff`; code must treat it as an output sentinel, not a valid destination.
- Block `FF` mixes two-byte EUC/JIS values with `0x00a1..0x00df` halfwidth values, so downstream encoding must honor this table contract.
- `KICONV_JA_CNV_U2_TO_EUCJPMS` evaluates arguments repeatedly and is not wrapped in `do { } while (0)`, so call sites should use simple expressions and braces in conditional contexts.
- Table correctness is data-sensitive: wrong literals compile cleanly but alter character conversion.

## Cross-Chunk References

Earlier chunks define the blocks referenced by `kiconv_ja_ucs2_to_euc16_index[]`, including `00..04`, `20..26`, `30`, `32..33`, `4E..9F`, and `E0..E7`. This chunk begins at the tail of block `E7`, observing only that final offsets `0x78..0xFF` are unmapped. The reverse-direction header `kiconv_ja_jis_to_unicode.h` contains related MS/CP932 override macros, so bidirectional behavior depends on keeping these exceptions aligned.
