# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/u8_textprep_data.h

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-6876, source bytes 262106, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_u8_textprep_data__bbab15de3cd9_research.md`
- chunk 2: lines 6877-13203, source bytes 262127, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_u8_textprep_data__e74ed2bf25b8_research.md`
- chunk 3: lines 13204-19890, source bytes 262141, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_u8_textprep_data__d6d7db338d88_research.md`
- chunk 4: lines 19891-25440, source bytes 262117, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_u8_textprep_data__edb2cdfb892c_research.md`
- chunk 5: lines 25441-31356, source bytes 262111, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_u8_textprep_data__f603586cce63_research.md`
- chunk 6: lines 31357-35374, source bytes 167141, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_u8_textprep_data__e74908e45082_research.md`

## Chunk Research

### Chunk 1: lines 1-6876

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/u8_textprep_data.h lines 1-6876

## Scope

This chunk covers the first 6,876 lines of `u8_textprep_data.h`, a generated/static Unicode UTF-8 text preparation data header in illumos. The full header is 35,374 lines; this chunk ends mid-definition of `u8_composition_b4_tbl`, so composition table coverage continues in later chunks.

Read verification: lines 1-6876 were read completely; SHA-256 over the exact chunk text is `af98d1202f0c756e9a1ebc1f526b8a50284904456d6743e1a3f6bed933829766`.

## File Role

`u8_textprep_data.h` supplies private lookup data for illumos UTF-8 validation/text preparation, normalization, composition/decomposition, combining-class lookup, and case conversion. This chunk defines the shared lookup-table contract and the complete combining-class lookup tables, then begins canonical composition lookup tables.

The companion public header `u8_textprep.h` exposes APIs and flags that depend on these tables: `u8_validate`, `u8_strcmp`, `u8_textprep_str`, Unicode version selectors `U8_UNICODE_320`/`U8_UNICODE_500`, and normalization/case flags.

## Declarations And Data

- Lines 1-67: CDDL and Unicode permission notices.
- Lines 68-75: include guard, `<sys/types.h>`, C++ wrapping.
- Lines 77-124: table traversal scheme. UTF-8 chars are treated as 4-byte keys; shorter encodings are left-padded.
- Lines 126-130: `u8_displacement_t { uint16_t tbl_id; uint16_t base; }`.
- Lines 132-141: sentinels `N_ == 0xff` for undefined entries and `FIL_ == 0xf7` for final-table character boundaries.
- Lines 143-216: `u8_common_b1_tbl[2][256]`.
- Lines 218-362: `u8_combining_class_b2_tbl[2][2][256]`.
- Lines 364-981: `u8_combining_class_b3_tbl[2][9][256]`.
- Lines 983-4732: `u8_combining_class_b4_tbl[2][55][256]`, storing direct canonical combining class values.
- Lines 4734-4803: `u8_composition_b1_tbl[2][256]`.
- Lines 4805-4881: `u8_composition_b2_tbl[2][1][256]`.
- Lines 4883-5768: `u8_composition_b3_tbl[2][5][256]`, including `0x8000`-tagged entries for later 16-bit fourth-byte tables.
- Lines 5770-6876: beginning of `u8_composition_b4_tbl[2][41][257]`.

## Control Flow

There is no executable code. Consumers perform data-driven trie lookup:

1. Convert each UTF-8 character into a 4-byte lookup key.
2. Use byte 1 in a `b1` table.
3. Use byte 2 in the selected `b2` table.
4. Use byte 3 in the selected `b3` table.
5. Use byte 4 in a `b4` table.

Combining-class lookup returns the class directly from `u8_combining_class_b4_tbl`. Composition/decomposition/case mappings use fourth-byte table entries as start/end offsets into final byte tables. Entries with `tbl_id >= 0x8000` select 16-bit fourth-byte tables defined later.

## State And Dependencies

All data in this chunk is `static const`; there is no mutable state. The outer `[2]` dimension represents Unicode 3.2.0 and Unicode 5.0.0.

Dependencies visible here:

- `<sys/types.h>` for `uchar_t` and `uint16_t`.
- `u8_textprep.h` for public APIs/flags.
- `usr/src/uts/common/sys/Makefile`, which exports `u8_textprep.h` and `u8_textprep_data.h`.
- Generated Unicode data from tools referenced as `PSARC/2007/149/materials/tools.tar.gz`.

## Risks

- This chunk ends inside `u8_composition_b4_tbl`; later chunks are required for complete composition behavior.
- `N_ == 0xff` must never be treated as a real table id.
- `0x8000` dispatch to 16-bit tables is required to avoid truncating final-table offsets.
- `[257]` fourth-byte tables rely on `index` and `index + 1` range lookup.
- Unicode version selection affects filesystem name normalization semantics, especially for ZFS-style normalized comparisons.
- Large `static const` tables can duplicate object data if broadly included.
- License notices combine CDDL and Unicode terms and must be preserved.

## Cross-Chunk References

- `u8_composition_b4_tbl` continues through line 8645.
- `u8_composition_b4_16bit_tbl` starts at line 8647.
- `u8_composition_final_tbl` starts at line 9004.
- Decomposition tables start at line 10667.
- Case-conversion tables start at line 27453.
- Macro cleanup and include guard closure occur at lines 35367-35374.

## Summary

Lines 1-6876 establish the Unicode textprep lookup format, provide complete combining-class data for Unicode 3.2.0 and 5.0.0, and begin canonical composition data. The encoded lookup path is central to UTF-8 normalization and filesystem name comparison through `u8_textprep.h`; main risks are sentinel handling, 8-bit versus 16-bit table dispatch, version consistency, and the mid-table chunk boundary.

### Chunk 2: lines 6877-13203

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/u8_textprep_data.h lines 6877-13203

## Scope

This chunk is a generated Unicode text-preparation data slice inside illumos `u8_textprep_data.h`. It contains no functions or public entry points; it is immutable table payload consumed by the UTF-8 textprep implementation described in the file header and implemented outside this header, primarily in `u8_textprep.c`.

The range starts in the middle of `u8_composition_b4_tbl[2][41][257]`, closes the byte-sized composition index table, includes the full 16-bit composition index table and full composition final-byte table, then begins decomposition lookup data through `u8_decomp_b4_tbl` table 27. The chunk ends before `u8_decomp_b4_tbl` table 27 is complete.

## APIs And Symbols

- `u8_composition_b4_tbl[2][41][257]`: tail of first Unicode-version subarray table 31 through table 40, then complete second Unicode-version subarray tables 0 through 40.
- `u8_composition_b4_16bit_tbl[2][5][257]`: fully defined here for composition final-table offsets that do not fit in `uchar_t`.
- `u8_composition_final_tbl[2][6623]`: fully defined here; packed UTF-8 bytes plus `FIL_` delimiters.
- `u8_decomp_b2_tbl[2][2][256]`: fully defined here; maps second byte to decomposition third-byte table ids or `N_`.
- `u8_decomp_b3_tbl[2][8][256]`: fully defined here as `u8_displacement_t { tbl_id, base }`.
- `u8_decomp_b4_tbl[2][118][257]`: starts here and continues after the chunk; this chunk ends mid-table 27.

## Control Flow And State

There is no executable control flow in this chunk. External consumers select Unicode version `[0]` or `[1]`, traverse b1/b2/b3/b4 tables, read adjacent b4 entries as `[start, end)` ranges, then decode bytes from the final table. High-bit b3 ids such as `0x8000` through `0x801D` route lookups to later 16-bit b4 tables.

All data is `static const`; there is no allocation, locking, mutation, reference counting, or runtime ownership.

## Dependencies

Depends on `uchar_t`, `uint16_t`, `u8_displacement_t`, `N_`, and `FIL_` from earlier in the header. It must stay synchronized with earlier composition b1/b2/b3 tables and later decomposition b4 16-bit/final tables. Runtime behavior is in `u8_textprep.c`.

## Risks And Invariants

The 257-entry b4-table width is critical because lookups read `index` and `index + 1`. Byte-sized b4 offsets must not exceed `uchar_t` capacity; larger offset ranges require the `0x8000` 16-bit-table convention. `N_` is valid only in index/displacement tables, while `FIL_` is an internal final-table delimiter, not string termination.

A single generated-data edit can silently alter Unicode normalization/composition behavior, so validation should come from regeneration and Unicode conformance tests rather than visual review.

## Cross-Chunk References

Earlier chunks define guards, sentinels, common b1 tables, combining-class data, and the start of composition tables. This chunk begins inside `u8_composition_b4_tbl` table 31 and ends inside `u8_decomp_b4_tbl` table 27. Later chunks continue decomposition b4 data and define `u8_decomp_b4_16bit_tbl`, `u8_decomp_final_tbl`, case conversion tables, and the header close.

### Chunk 3: lines 13204-19890

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/u8_textprep_data.h lines 13204-19890

## Scope

This report covers lines 13204-19890 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/u8_textprep_data.h` for `learn_fs` subset A. The file is generated Unicode text-preparation data. This chunk begins in the middle of `u8_decomp_b4_tbl[0][27]`, covers the remainder of the Unicode 3.2.0 decomposition b4 table from table 28 through table 117, crosses into the Unicode 5.0.0 half at line 16361, and ends in the middle of `u8_decomp_b4_tbl[1][100]`.

The chunk contains no executable functions or preprocessor declarations; its semantics come from:

`static const uchar_t u8_decomp_b4_tbl[2][118][257]`.

## Public Surface And APIs

No new public API is declared here. The data supports `u8_validate()`, `u8_strcmp()`, and `u8_textprep_str()` from `u8_textprep.h`.

Relevant flags include `U8_STRCMP_NFD`, `U8_STRCMP_NFC`, `U8_STRCMP_NFKD`, `U8_STRCMP_NFKC`, and `U8_TEXTPREP_*` aliases. `U8_UNICODE_320`, `U8_UNICODE_500`, and `U8_UNICODE_LATEST` select the first table dimension.

Visible downstream users include ZFS ZAP name normalization, ZFS vnode name validation/comparison, pcfs long-name case folding, and SMB string comparison/validation paths.

## Data Layout

This is the 8-bit decomposition fourth-level offset table. Each b4 row has 257 entries because lookup reads `entry[byte4]` and `entry[byte4 + 1]` as a half-open range into `u8_decomp_final_tbl`.

Within this range:

- Lines 13204-13209 finish Unicode 3.2.0 fourth byte table 27.
- Lines 13210-16359 cover complete Unicode 3.2.0 tables 28-117.
- Lines 16360-16361 close version group 0 and open version group 1.
- Lines 16362-19861 cover complete Unicode 5.0.0 tables 0-99.
- Lines 19862-19890 start Unicode 5.0.0 table 100.

Values are monotonically nondecreasing offsets within each row. Repeated values represent empty decomposition ranges.

## Control Flow

There is no local control flow. Runtime lookup is table-driven:

1. Textprep code selects b1/b2/b3 tables from UTF-8 bytes.
2. `u8_decomp_b3_tbl` selects a b4 table id.
3. This table supplies `start_index` and `end_index`.
4. Non-empty ranges index bytes in `u8_decomp_final_tbl`.
5. Other tables handle 16-bit offsets, composition, validation, and case mapping.

The data is immutable and has no locks, allocation, mutation, or error handling.

## State, Dependencies, Risks

State is static read-only kernel data. Correctness depends on cross-table alignment among `u8_common_b1_tbl`, `u8_decomp_b2_tbl`, `u8_decomp_b3_tbl`, `u8_decomp_b4_tbl`, `u8_decomp_b4_16bit_tbl`, and `u8_decomp_final_tbl`.

Key risks:

- A shifted or corrupted initializer can silently alter filesystem name normalization.
- Both chunk endpoints split initializer rows, so this chunk is not standalone C.
- The 8-bit offset representation requires values to remain <= 255; larger rows must use `u8_decomp_b4_16bit_tbl`.
- Version dimensions must remain aligned with `U8_UNICODE_320 == 0` and `U8_UNICODE_500 == 1`.

## Cross-Chunk References

Earlier chunks cover the header, type definitions, common/decomposition b1-b3 tables, and the start of `u8_decomp_b4_tbl` through table 27. Later chunks must cover the rest of table 100, tables 101-117, `u8_decomp_b4_16bit_tbl`, `u8_decomp_final_tbl`, and later case-conversion tables.

### Chunk 4: lines 19891-25440

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/u8_textprep_data.h lines 19891-25440

## Scope

This chunk is part of the generated Unicode text-preparation data used by illumos kernel UTF-8 normalization and case handling. It is in subset A because `sources/os/illumos/illumos-gate` is included by `Docs/research_subset_a.md`.

The chunk contains no executable functions. It spans the end of the 8-bit decomposition fourth-byte index table, the complete 16-bit decomposition fourth-byte index table, and the beginning of the large final decomposition byte table.

## APIs And Exports

- Continues `static const uchar_t u8_decomp_b4_tbl[2][118][257]`, which began before this chunk at line 12228. Lines 19891-20493 cover the tail of the first Unicode-version half: the end of fourth-byte table 100 and full fourth-byte tables 101-117.
- Defines `static const uint16_t u8_decomp_b4_16bit_tbl[2][30][257]` at lines 20495-22600. This table is fully contained in the chunk.
- Defines the start of `static const uchar_t u8_decomp_final_tbl[2][19370]` at line 22602. The first 19,370-byte subarray closes at line 25026; the second subarray starts at line 25027 and continues past line 25440.
- Does not define or export public C functions. Public consumers see this data indirectly through the `u8_textprep.h` APIs, especially `u8_textprep_str()`, `u8_strcmp()`, and normalization/case flags such as `U8_TEXTPREP_NFD`, `U8_TEXTPREP_NFC`, `U8_TEXTPREP_NFKD`, `U8_TEXTPREP_NFKC`, `U8_TEXTPREP_TOUPPER`, and `U8_TEXTPREP_TOLOWER`.

## Data Layout

The file-level comment describes UTF-8 code points as four-byte lookup keys. Earlier b1, b2, and b3 tables select a fourth-byte table, and the fourth-byte value indexes adjacent slots in that selected b4 table. The value at slot `b4` is the start index into `u8_decomp_final_tbl`; the value at slot `b4 + 1` is the end index.

The table choice is split by index width:

- `u8_decomp_b4_tbl` stores byte-sized final-table offsets for ranges whose decomposition payload offsets fit in `uchar_t`.
- `u8_decomp_b4_16bit_tbl` stores 16-bit final-table offsets when the b3 table marks the selected b4 table id with `0x8000`.
- Both b4 table families have `257` entries per fourth-byte table so every possible fourth-byte index can read a `[start, end)` pair without a special last-byte case.

The final table stores raw UTF-8 decomposition bytes. In the visible payload, `0xF6` appears frequently as a generated separator/end marker between decomposition sequences, while `0xF5` appears much less often in multi-result/control encodings. The public filler macro near the top of the file is `0xF7`, but this chunk's visible final-table bytes do not contain `0xF7`.

## Control Flow

There is no local runtime control flow. Runtime lookup follows the data contract documented in the header:

1. Select Unicode data version `[0]` for Unicode 3.2.0 or `[1]` for Unicode 5.0.0.
2. Use prior chunks' `u8_common_b1_tbl`, `u8_decomp_b2_tbl`, and `u8_decomp_b3_tbl` to find a fourth-byte table id and optional displacement/base metadata.
3. If the b4 table id has the high `0x8000` bit set, clear that bit and index `u8_decomp_b4_16bit_tbl`; otherwise index `u8_decomp_b4_tbl`.
4. Use the returned `[start_index, end_index)` range to copy or interpret bytes from `u8_decomp_final_tbl[version]`.

The first version's final decomposition payload is complete in this chunk, while the second version's payload is only partially present here.

## State And Dependencies

All data is immutable `static const` storage in a guarded kernel header. There is no allocation, locking, mutation, or per-call state in this chunk.

Dependencies visible from the surrounding file and public header:

- `<sys/types.h>` supplies `uchar_t` and fixed-width integer types used by the tables.
- `u8_displacement_t`, defined near the top of this file, is used by earlier b3 decomposition tables to decide whether the lookup should use 8-bit or 16-bit b4 offset tables.
- `sys/u8_textprep.h` declares the public Unicode conversion and text-preparation APIs and the version constants `U8_UNICODE_320`, `U8_UNICODE_500`, and `U8_UNICODE_LATEST`.
- Kernel files in ZFS, pcfs, and SMB paths call `u8_textprep_str()` or use the text-prep flags for normalized/case-insensitive name handling; those consumers depend on this generated table data even though the table symbols are header-local.

## Risks

- Manual edits are high risk: adjacent b4 slots form `[start, end)` ranges into the final table, so changing one value can corrupt one or more decompositions.
- The 8-bit and 16-bit b4 tables are selected by high-bit metadata in earlier `u8_decomp_b3_tbl` entries. If those earlier ids and these table dimensions diverge, lookups can read the wrong offset family.
- `u8_decomp_final_tbl[2][19370]` has exact per-version lengths. Inserting or deleting bytes in the first final-table subarray would shift every later offset and can also break the fixed initializer length.
- The chunk boundary is in the middle of the second version's final-table payload at line 25440, so this chunk alone cannot validate closure, final byte count, or trailing table declarations.
- Because ZFS and pcfs use text preparation for filesystem name normalization/case behavior, corrupted decomposition data can surface as lookup mismatches, normalization instability, or incompatible on-disk name comparison semantics.

## Cross-Chunk References

- Earlier chunks define the header guard, constants, `u8_displacement_t`, common b1 tables, decomposition b2/b3 tables, and the start of `u8_decomp_b4_tbl`. This chunk starts inside fourth-byte table 100 and relies on those prior declarations.
- This chunk closes `u8_decomp_b4_tbl` at line 20493 and fully covers `u8_decomp_b4_16bit_tbl`, making it the bridge between earlier decomposition trie selection and the final byte payload.
- Later chunks continue `u8_decomp_final_tbl[1]` after line 25440 and must close the full final table and the header. They are needed for complete Unicode 5.0.0 decomposition coverage and whole-file validation.

### Chunk 5: lines 25441-31356

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/u8_textprep_data.h lines 25441-31356

## Scope

This report covers lines 25441-31356 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/u8_textprep_data.h` for `learn_fs` subset A. The file is generated Unicode text-preparation data used by illumos UTF-8 normalization and case-mapping routines. The exact requested range was read completely.

This chunk is not syntactically standalone C. It starts in the middle of `u8_decomp_final_tbl[1]`, crosses complete case-mapping selector tables, and ends in the middle of `u8_tolower_final_tbl[1]`.

## Public Surface And APIs

No public API is declared here. The chunk provides static read-only data behind the public interfaces declared in `u8_textprep.h`:

- `u8_validate(char *, size_t, char **, int, int *)`
- `u8_strcmp(const char *, const char *, size_t, int, size_t, int *)`
- `u8_textprep_str(char *, size_t *, char *, size_t *, int, size_t, int *)`

The visible API selectors relevant to this chunk are `U8_TEXTPREP_TOLOWER`, `U8_TEXTPREP_NFD`, `U8_TEXTPREP_NFC`, `U8_TEXTPREP_NFKD`, `U8_TEXTPREP_NFKC`, and the Unicode-version selectors `U8_UNICODE_320 == 0`, `U8_UNICODE_500 == 1`, and `U8_UNICODE_LATEST == U8_UNICODE_500`.

Visible filesystem consumers in subset A include ZFS ZAP name normalization through `zap_normalize()` in `zap_micro.c` and pcfs long filename case folding in `pc_vnops.c`. Those callers invoke `u8_textprep_str()` and do not address this header's tables directly.

## Data Layout

The chunk covers these enclosing declarations:

- Lines 25441-27451: continuation and close of `static const uchar_t u8_decomp_final_tbl[2][19370]`, specifically the Unicode 5.0.0 final decomposition payload.
- Lines 27453-27597: complete `static const uchar_t u8_case_common_b2_tbl[2][2][256]`.
- Lines 27599-28264: complete `static const u8_displacement_t u8_tolower_b3_tbl[2][5][256]`.
- Lines 28266-30791: complete `static const uchar_t u8_tolower_b4_tbl[2][36][257]`.
- Lines 30793-31356: start and most of `static const uchar_t u8_tolower_final_tbl[2][2299]`, covering all of version 0 and most of version 1 before the array closes just after this chunk.

The final-table bytes are UTF-8 replacement payloads. `0xF6` appears as an in-band separator between mapped UTF-8 characters in final tables. The file-level comments define `0xF7` as `U8_TBL_ELEMENT_FILLER`, but this chunk's final payloads mainly use raw UTF-8 bytes plus `0xF6` separators.

The `u8_case_common_b2_tbl` table is a second-byte selector shared by lower- and upper-case conversion. It maps UTF-8 byte 2 to a compact b3-table id or `N_` (`0xff`) for no case mapping.

The `u8_tolower_b3_tbl` entries are `u8_displacement_t { tbl_id, base }` pairs. `tbl_id == N_` means no lower-case mapping for that third-byte position. Otherwise the id selects a row in `u8_tolower_b4_tbl`, while `base` participates in computing the final-table range.

The `u8_tolower_b4_tbl` rows each have 257 entries so lookup can read both `[byte4]` and `[byte4 + 1]`. Adjacent offset values define a half-open slice into `u8_tolower_final_tbl[version]`; repeated adjacent offsets mean no payload for that byte value.

## Control Flow

There is no executable control flow in this chunk. Runtime behavior is table-driven:

1. A caller asks `u8_textprep_str()` or `u8_strcmp()` for normalization, case folding, or comparison.
2. For decomposition, earlier b1/b2/b3/b4 tables select a byte range in `u8_decomp_final_tbl`; this chunk supplies the latter part of the Unicode 5.0.0 payload.
3. For lowercase mapping, `u8_common_b1_tbl` and `u8_case_common_b2_tbl` select a lower-case b3 row.
4. `u8_tolower_b3_tbl` supplies a b4 table id and base for the third byte.
5. `u8_tolower_b4_tbl` supplies adjacent offsets for the fourth byte.
6. The implementation copies bytes from `u8_tolower_final_tbl[version][start..end)` into the output stream, interpreting final-table separators according to the generated table format.

The chunk has no locks, allocations, branches, or error handling. Errors surface in consumers only when the surrounding textprep code encounters invalid UTF-8, unsupported mappings, or insufficient output space.

## State And Dependencies

All state here is `static const` kernel data. Correctness depends on cross-table alignment:

- `u8_case_common_b2_tbl`, `u8_tolower_b3_tbl`, and `u8_tolower_b4_tbl` must agree on table ids for both Unicode versions.
- Each `u8_tolower_b4_tbl` row must have exactly 257 monotonic, in-range offsets so `[byte4 + 1]` is valid.
- Offsets produced by `u8_tolower_b4_tbl` must remain within `u8_tolower_final_tbl[2][2299]`.
- Decomposition offsets from earlier chunks must remain within `u8_decomp_final_tbl[2][19370]`.
- The first dimension must continue to match `U8_UNICODE_320` and `U8_UNICODE_500`.
- `N_` depends on the earlier macro `U8_TBL_ELEMENT_NOT_DEF == 0xff`, and b3 entries depend on the earlier `u8_displacement_t` typedef.

The data ultimately derives from Unicode data files noted in the header comments and accompanying Unicode third-party license files.

## Risks And Invariants

The primary risk is generated-data drift. A shifted byte in `u8_decomp_final_tbl` or `u8_tolower_final_tbl` would keep the C initializer valid while changing filesystem name normalization or case-insensitive matching behavior.

Boundary risk is high because the chunk starts and ends inside final payload arrays. Earlier chunks must provide the beginning of `u8_decomp_final_tbl[1]`; the next chunk must provide the tail and closing brace of `u8_tolower_final_tbl[1]` plus the following upper-case tables.

Offset-table invariants are critical. If a b4 row is not monotonic, if it lacks the 257th sentinel entry, or if an offset exceeds the final table length, lookup can produce wrong output or out-of-bounds reads in low-level textprep code.

Compatibility risk is filesystem-visible. ZFS and pcfs can use these mappings when comparing or folding names, so changing data generation can affect on-disk name lookup semantics even though this header has no executable code.

## Cross-Chunk References

Earlier chunks should cover the header comments, `u8_displacement_t`, `N_`, common b1 tables, decomposition selector tables, and the start of `u8_decomp_final_tbl`. This chunk closes decomposition final data and introduces lower-case mapping tables.

The following chunk must finish `u8_tolower_final_tbl[1]` and cover `u8_toupper_b3_tbl`, `u8_toupper_b4_tbl`, and `u8_toupper_final_tbl`. The final per-file report should merge this chunk with both adjacent chunks because the selector tables in this chunk are only meaningful when paired with the final-table bytes that begin before and continue after this range.

### Chunk 6: lines 31357-35374

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/u8_textprep_data.h lines 31357-35374

## Scope

This chunk is the final ordered slice of `u8_textprep_data.h`, a generated Unicode text-preparation data header in the illumos kernel tree. It is in subset A because `sources/os/illumos/illumos-gate` is included by `Docs/research_subset_a.md`.

The chunk contains no executable functions. It closes the `u8_tolower_final_tbl` data started before this range, then defines the complete uppercase conversion lookup tables and closes the header guard.

## APIs And Exports

- Completes the tail of `static const uchar_t u8_tolower_final_tbl[2][2299]` at lines 31357-31374. The visible tail maps lower-case outputs for fullwidth Latin lower-case letters and Deseret lower-case code points.
- Defines `static const u8_displacement_t u8_toupper_b3_tbl[2][5][256]` at lines 31376-32041. This is the third-byte dispatch table for uppercase conversion for two Unicode data versions: index `0` is Unicode 3.2.0 and index `1` is Unicode 5.0.0, as described in the file header.
- Defines `static const uchar_t u8_toupper_b4_tbl[2][39][257]` at lines 32043-34778. Each fourth-byte table has 257 entries so consumers can read adjacent start/end offsets for a fourth-byte value and the next value.
- Defines `static const uchar_t u8_toupper_final_tbl[2][2318]` at lines 34780-35365. This byte pool stores the UTF-8 uppercase replacement sequences addressed by the `b4` offset tables.
- Undefines the local shorthand macros `N_` and `FIL_`, closes the optional C++ linkage block, and closes `_SYS_U8_TEXTPREP_DATA_H` at lines 35367-35374.

All data symbols are `static const`, so this header provides compile-unit-local data to files that include it rather than exporting linker-visible symbols.

## Data Layout

The lookup structure follows the multi-level scheme documented near the top of the file:

- The shared `u8_common_b1_tbl` and `u8_case_common_b2_tbl`, defined in earlier chunks, select a case-conversion third-byte table.
- `u8_toupper_b3_tbl` stores `u8_displacement_t` entries with a `tbl_id` and `base`. `N_` (`0xff`) marks undefined/non-mapping entries.
- `u8_toupper_b4_tbl` stores offsets relative to the selected `base`. Consumers use the current and next fourth-byte entries as `[start, end)` bounds into the final byte table.
- `u8_toupper_final_tbl` stores packed UTF-8 output bytes. Entries can be one or more UTF-8 characters depending on the Unicode uppercase mapping.

The uppercase final table includes mappings across Latin, Greek, Cyrillic, Armenian, Latin Extended Additional, Greek Extended, Roman numerals, circled letters, Glagolitic, Coptic, Georgian, fullwidth Latin, and Deseret ranges. The two outer version slots differ: Unicode 5.0.0 includes mappings not present in the Unicode 3.2.0 slot, for example later-script additions visible in the second final-table block.

## Control Flow

There is no direct control flow in this chunk. Runtime control flow is table-driven:

1. A caller requests uppercase preparation or comparison through public APIs such as `u8_textprep_str()` or `u8_strcmp()` with `U8_TEXTPREP_TOUPPER` / `U8_STRCMP_CI_UPPER`.
2. The implementation validates and parses a UTF-8 character as a four-byte lookup key.
3. Earlier `b1`/`b2` tables select the `u8_toupper_b3_tbl` row for the first and second UTF-8 bytes.
4. The third byte selects a `u8_displacement_t` entry. If it is not `N_`, its `tbl_id` selects a `u8_toupper_b4_tbl` row and its `base` contributes to the final-table offset calculation.
5. The fourth byte selects adjacent offset entries in the `b4` row; the byte span in `u8_toupper_final_tbl` is emitted as the uppercase mapping.

The 257-entry `b4` rows are important to this control flow because they allow `end_index = row[fourth_byte + 1]` without a special case for most values.

## State And Dependencies

All state in the chunk is immutable static storage. There is no allocation, locking, mutation, I/O, or error handling in the chunk itself.

Dependencies visible in this slice and adjacent header context:

- `uchar_t`, `uint16_t`, and related base types come from `<sys/types.h>`.
- `u8_displacement_t` is defined earlier in this header as `{ uint16_t tbl_id; uint16_t base; }`.
- `N_` is the local alias for `U8_TBL_ELEMENT_NOT_DEF` (`0xff`), defined earlier and undefined at the end of this chunk.
- `FIL_` is the local alias for `U8_TBL_ELEMENT_FILLER` (`0xf7`), although this final uppercase slice mainly uses raw UTF-8 bytes and zero padding.
- Public flags and entry points are declared in `u8_textprep.h`: `U8_TEXTPREP_TOUPPER`, `U8_TEXTPREP_TOLOWER`, `U8_UNICODE_320`, `U8_UNICODE_500`, `U8_UNICODE_LATEST`, `u8_validate()`, `u8_strcmp()`, and `u8_textprep_str()`.

Visible kernel consumers include ZFS name normalization, pcfs long filename case folding, and SMB client string comparisons. For example, ZFS documents `U8_TEXTPREP_TOUPPER` as a valid normalization flag for normalized ZAP names, while pcfs uses `u8_textprep_str(..., U8_TEXTPREP_TOLOWER, U8_UNICODE_LATEST, ...)` for foldcase paths.

## Risks

- The data is generated and offset-coupled. Manual edits to any `b3`, `b4`, or final-table byte can silently corrupt case-insensitive filesystem lookup semantics.
- `u8_toupper_b3_tbl` references `u8_toupper_b4_tbl` rows by small integer IDs and final-table bases. A mismatched table ID or base can redirect a code point to unrelated UTF-8 bytes.
- `u8_toupper_b4_tbl` uses adjacent offsets, so every row must preserve exactly 257 entries. Missing or extra values shift later offsets and can cause wrong spans or out-of-bounds reads in consumers.
- Unicode version indexing must stay aligned across all tables. Callers using `U8_UNICODE_LATEST` rely on slot `1` consistently meaning Unicode 5.0.0 across the common, lower, upper, decomposition, and composition tables.
- Filesystem name normalization depends on stable mappings. Regenerating these tables with a different Unicode version or changed case mapping rules can alter on-disk name hashes or case-insensitive comparison behavior.

## Cross-Chunk References

- Earlier chunks define the common first-byte table, case common second-byte table, and the full `u8_tolower_b3_tbl`, `u8_tolower_b4_tbl`, and most of `u8_tolower_final_tbl`.
- This chunk starts in the middle of `u8_tolower_final_tbl`; the declaration and most lower-case mapping payload are in the previous chunk.
- This chunk completes the file, so there is no later chunk for `u8_textprep_data.h`. The final per-file report should merge this chunk with prior chunks rather than being created here.
