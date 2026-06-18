# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp949.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-3981, source bytes 262119, report `Docs/researches/chunks/chunk_sources_os_linux_linux_stable_fs_nls_nls_cp949_c_1_1_3981_849ae9e8643f_research.md`
- chunk 2: lines 3982-8200, source bytes 262112, report `Docs/researches/chunks/chunk_sources_os_linux_linux_stable_fs_nls_nls_cp949_c_2_3982_8200_45630c500721_research.md`
- chunk 3: lines 8201-12440, source bytes 262096, report `Docs/researches/chunks/chunk_sources_os_linux_linux_stable_fs_nls_nls_cp949_c_3_8201_12440_4a1e78a40910_research.md`
- chunk 4: lines 12441-13947, source bytes 88972, report `Docs/researches/chunks/chunk_sources_os_linux_linux_stable_fs_nls_nls_cp949_c_4_12441_13947_9a944806100b_research.md`

## Chunk Research

### Chunk 1: lines 1-3981

# Chunk Research: sources/os/linux/linux-stable/fs/nls/nls_cp949.c lines 1-3981

## Scope

This chunk covers the file prologue, kernel/NLS includes, and the first large block of CP949-to-Unicode translation data. It is generated table content, not procedural filesystem code. The range ends in the middle of the `c2u_F1` initializer, so `c2u_F1` is incomplete in this chunk and must be joined with the next chunk for a complete table view.

## APIs and Data Definitions

- Includes: `<linux/module.h>`, `<linux/kernel.h>`, `<linux/string.h>`, `<linux/nls.h>`, and `<linux/errno.h>`. The direct type dependency visible here is `wchar_t`, used for Unicode code points in the charset-to-Unicode pages.
- Defines static read-only arrays named `c2u_XX`, each representing one CP949 lead-byte page and indexed by the second byte. The visible completed pages are `c2u_81` through `c2u_F0`, with no `c2u_C9` page in this range.
- Each array is declared as `static const wchar_t c2u_XX[256]`, but several initializers intentionally provide fewer than 256 explicit literals; C zero-initialization fills the remainder. This appears in compact sparse pages such as `c2u_A2`, `c2u_A6`, `c2u_A7`, `c2u_AA`, `c2u_AB`, `c2u_AC`, and `c2u_AD`-`c2u_AF`.
- The chunk starts `c2u_F1` at line 3968 and includes entries only through second-byte range `0x60-0x67` at line 3981. The visible part of `c2u_F1` has 104 explicit entries, all `0x0000`.

## Table Semantics

- `0x0000` is used as the invalid/unmapped sentinel for byte pairs that are not assigned in CP949. This is especially common in control-byte regions, separator gaps, and sparse Hanja/compatibility pages.
- Pages `0x81`-`0xA0` mostly map CP949 extension byte pairs to Hangul syllables in the Unicode Hangul Syllables block, beginning at values such as `0xAC02`.
- Pages `0xA1`-`0xA9` mix Hangul extension entries with punctuation, fullwidth ASCII, Hangul compatibility jamo, Greek, box drawing, units, enclosed forms, and other compatibility symbols.
- Pages `0xAA` and `0xAB` contain Japanese Hiragana and Katakana ranges after CP949 extension entries.
- Page `0xAC` includes Cyrillic upper/lowercase blocks after extension entries.
- Pages `0xCA` and later in this chunk carry Hanja/CJK ideographs and compatibility ideographs, with many zero-filled low-byte slots before valid mappings begin around second byte `0xA1`.
- Many completed pages follow the same lead-byte layout: low second-byte positions are zero-filled, then assigned code points appear in the printable/trailing-byte ranges, followed by a final zero at `0xFF`.

## Control Flow

There is no executable control flow in lines 1-3981. The only "flow" is data lookup implied by the table shape:

1. A later decoder will select a page by CP949 lead byte.
2. It will index that page by the following byte.
3. A nonzero `wchar_t` result is a Unicode mapping; `0x0000` indicates an invalid or unmapped byte pair.

The actual `char2uni`, `uni2char`, `struct nls_table`, module init/exit, and reverse Unicode-to-charset tables are outside this chunk.

## State and Lifetime

- All visible state is `static const` translation data with internal linkage.
- The arrays are immutable after compilation and safe for concurrent lookup without locking.
- There is no allocation, reference counting, module registration, or mutable global state in this chunk.

## Dependencies

- Kernel NLS infrastructure is implied by `<linux/nls.h>` and by the naming/layout expected by the later conversion callbacks.
- Module infrastructure is included here but only used in later chunks for registration metadata and init/exit functions.
- The generated table source is documented as Microsoft's CP949 Unicode mapping data in the file comment.

## Risks and Invariants

- Correctness is entirely table-driven. A single wrong literal, missing page pointer, or shifted initializer would silently corrupt filename/metadata charset conversion for Korean CP949/EUC-KR users.
- Sparse initializers rely on C zero-fill semantics. This is valid but important: changing these tables mechanically without preserving implicit trailing zeroes can alter invalid-byte behavior.
- `0x0000` cannot represent U+0000 as a valid decoded result here; it is treated as "no mapping" by the expected decoder contract.
- The chunk boundary is risky for automated analysis because it splits `c2u_F1`; consumers must not treat line 3981 as the end of that table.
- Because the data is generated, manual edits should be avoided unless validated against the authoritative CP949 mapping and the reverse `u2c_*` tables in later chunks.

## Cross-Chunk References

- `c2u_F1` continues after line 3981 and completes in the next chunk.
- Later chunks define the remaining `c2u_*` pages, reverse `u2c_*` Unicode-to-CP949 tables, page pointer tables, case conversion tables, and the NLS callback functions that consume this data.
- The merge report should connect this chunk's `c2u_*` data to the later `char2uni()` implementation and `page_charset2uni`/equivalent page selection table, because this chunk alone does not show how the arrays are selected at runtime.

### Chunk 2: lines 3982-8200

# Chunk Research: sources/os/linux/linux-stable/fs/nls/nls_cp949.c lines 3982-8200

## Scope

This chunk is within subset A (`Docs/research_subset_a.md`) under `sources/os/linux/linux-stable`. I read the requested range completely. Adjacent context was used only to identify the containing declarations and the later converter callbacks that consume these tables.

The range is generated/static CP949/EUC-KR conversion data. It has no function bodies, branches, locks, allocation, or direct filesystem operations of its own.

## APIs And Symbols

All symbols in this chunk are file-local `static const` lookup tables backing the NLS module:

- Tail of `c2u_F1[256]`: the chunk begins inside this charset-to-Unicode page table at low-byte comments `0x68-0x6F` and continues through the close at line 4002.
- Complete charset-to-Unicode page tables `c2u_F2[256]` through `c2u_FD[256]`: these map CP949 lead bytes `0xF2` through `0xFD` plus trailing byte index to Unicode `wchar_t` values.
- Complete `page_charset2uni[256]`: pointer dispatch table that maps the first CP949 byte to a `c2u_*` page. It references `c2u_81` through `c2u_FD`, leaves unsupported lead-byte slots as `NULL`, and notably has `NULL` for `0xC9`, `0xFE`, and `0xFF`.
- Complete Unicode-to-charset page tables from `u2c_01[512]` through `u2c_79[512]`, with gaps matching declared Unicode high-byte pages: `01`, `02`, `03`, `04`, `11`, `20`-`26`, `30`-`33`, and `4E`-`79`.
- Start of `u2c_7A[512]`: the chunk includes the declaration and entries through Unicode low-byte comment `0x10-0x13`; the table continues in the next chunk.

There are no exported symbols here. The public module surface is created later by `struct nls_table table`, whose `.uni2char` and `.char2uni` callbacks consume these static arrays.

## Data Model And State

The data is immutable conversion state:

- `c2u_*` entries are indexed by the second CP949 byte and store Unicode code points. `0x0000` is the invalid/unmapped sentinel.
- `page_charset2uni[first_byte]` chooses the correct `c2u_*` table for two-byte decoding; `NULL` means that byte is not a double-byte lead in this table.
- `u2c_*` entries are two output bytes per Unicode low-byte index, so each 512-byte table covers one Unicode high-byte page. A pair of `0x00, 0x00` is the unmapped sentinel.
- The tables include compatibility/private mapping values visible in this range, such as Unicode compatibility ideograph/codepoint range entries around `F9xx` and `FAxx`, which must remain synchronized with the reverse `u2c_*` data.

There is no mutable global state, reference counting, initialization side effect, or teardown behavior in the chunk.

## Control Flow

There is no local executable control flow. Effective runtime flow, from adjacent context, is table-driven:

- Decode path: `char2uni()` reads one or two input bytes, uses `page_charset2uni[ch]`, then returns `charset2uni[cl]` when the page exists and `cl != 0`; `0x0000` returns `-EINVAL`. If no page exists, it treats the first byte as a one-byte character.
- Encode path: `uni2char()` splits a Unicode `wchar_t` into high and low bytes, selects `page_uni2charset[ch]`, then returns the two bytes at `cl * 2`; `0x00,0x00` returns `-EINVAL`. If the Unicode high byte is zero and the low byte is nonzero, it emits one byte.
- This chunk supplies many of the pages selected by those two dispatch arrays; it does not itself perform bounds checks or error handling.

## Dependencies

Compile-time dependencies come from the wider file:

- Kernel NLS types and API definitions, including `wchar_t`, `struct nls_table`, `register_nls()`, and `unregister_nls()`.
- The later `page_uni2charset[256]` table depends on the `u2c_*` symbols defined here.
- The later `char2uni()` and `uni2char()` callbacks depend on the sentinel conventions and exact 256/512-entry sizing of these arrays.

No external libraries, filesystem internals, block-layer APIs, or VFS objects are used directly in this chunk.

## Risks And Invariants

- The chunk is high-risk to edit manually: a single literal change can silently corrupt filename transcoding for CP949/EUC-KR mounts.
- `0x0000` in `c2u_*` and `0x00,0x00` in `u2c_*` are semantic sentinels, not ordinary data.
- Table sizes and index formulas are coupled to callers: `c2u_*` must have 256 `wchar_t` entries; `u2c_*` must have 512 bytes because callers index `cl * 2` and `cl * 2 + 1`.
- The chunk begins and ends inside table symbols, so whole-symbol validation requires adjacent chunks.
- Round-trip correctness depends on consistency between the forward `c2u_*` tables and reverse `u2c_*` tables across the whole file, not only this line range.
- Invalid lead-byte behavior is determined by `page_charset2uni`: unsupported double-byte lead bytes fall back to single-byte decoding in `char2uni()`, while invalid mapped entries return `-EINVAL`.

## Cross-Chunk References

- Previous chunk: defines earlier `c2u_*` tables and the start of `c2u_F1`; this chunk starts inside `c2u_F1`.
- This chunk: completes the high CP949 forward mapping pages through `c2u_FD`, defines the forward dispatch table, defines many reverse Unicode pages, and starts `u2c_7A`.
- Next chunk: continues and closes `u2c_7A`, then defines the remaining reverse `u2c_*` pages.
- Final chunk/file tail: defines `page_uni2charset`, ASCII case tables, `uni2char()`, `char2uni()`, `struct nls_table table`, module init/exit, and module metadata.

### Chunk 3: lines 8201-12440

# Chunk Research: sources/os/linux/linux-stable/fs/nls/nls_cp949.c lines 8201-12440

Scope: `Docs/research_subset_a.md`, source tree `sources/os/linux/linux-stable`.

## Chunk Role

This chunk is static Unicode-to-CP949 mapping data for the Linux NLS `cp949` module. It contains no executable functions, locks, allocations, or module registration logic. Its exported effect is through later lookup wiring: `uni2char()` indexes `page_uni2charset[ch]`, then reads two bytes from the selected `u2c_XX` table at `cl * 2` and `cl * 2 + 1`.

The chunk begins inside `u2c_7A` and ends inside `u2c_C6`. Whole tables introduced in this range are `u2c_7B` through `u2c_C6`; `u2c_7A` starts in the prior chunk and `u2c_C6` continues in the next chunk.

## APIs And Data Contracts

- `static const unsigned char u2c_XX[512]`: each table maps a Unicode page `0xXX00..0xXXff` to 256 two-byte CP949/EUC-KR output sequences.
- Indexing contract: for Unicode `uni`, high byte `ch = (uni >> 8) & 0xff` chooses `u2c_ch` through `page_uni2charset[]`; low byte `cl = uni & 0xff` chooses a two-byte pair.
- Sentinel contract: `0x00, 0x00` means "unmapped"; later `uni2char()` returns `-EINVAL` when the selected pair is all zero.
- Nonzero pairs are emitted as exactly two bytes. There is no single-byte ASCII path through these tables; ASCII is handled by `uni2char()` only when no page table exists and `ch == 0 && cl`.

## Data Covered

- Partial `u2c_7A`: lines 8201-8261 cover the remainder of Unicode page `0x7A`, with sparse mappings and many zero sentinels.
- Sparse CJK-extension pages: `u2c_7B` through `u2c_9F` are mostly sparse tables with many unmapped entries. Within the exact chunk, these pages include 1,861 mapped pairs and 5,624 zero pairs.
- Hangul syllable pages: `u2c_AC` through `u2c_C5` are dense, fully mapped tables in this chunk. They cover Unicode pages from the Hangul syllables block beginning at `U+AC00`.
- Partial `u2c_C6`: lines 12405-12440 cover offsets `0x00..0x87` of Unicode page `0xC6`, all mapped in this partial range; the table continues after the chunk.

The byte patterns in the dense Hangul region show contiguous CP949 assignments such as `0xB0,0xA1` onward in `u2c_AC`, continuing into lead-byte ranges `0x9D`, `0x9E`, and `0x9F` by `u2c_C5`/`u2c_C6`. This is generated lookup data, not hand-coded control flow.

## Control Flow

No local control flow exists in this chunk. Runtime flow is external:

1. `uni2char()` receives a Unicode `wchar_t`.
2. It selects `page_uni2charset[ch]`.
3. If the selected pointer names one of the tables in this chunk, it copies the two bytes at the low-byte offset.
4. If both bytes are zero, conversion fails with `-EINVAL`; otherwise conversion succeeds with length `2`.

The correctness of this chunk therefore depends on table shape, table pointer placement, and sentinel consistency.

## State And Dependencies

- State is immutable `.rodata`: all arrays are `static const`.
- There is no per-call, per-mount, global mutable, or thread-local state in the chunk.
- Internal dependency: `page_uni2charset[]` later in the file must reference these arrays at indices matching their suffixes, for example index `0x7B` must reference `u2c_7B`.
- External dependencies are the Linux NLS interface and error semantics used by later code: `<linux/nls.h>` for `struct nls_table` and `<linux/errno.h>` for `-EINVAL`/`-ENAMETOOLONG`.

## Risks And Edge Cases

- Table truncation or misalignment is the primary risk. Each complete `u2c_XX` table must contain exactly 512 bytes, preserving the two-byte-per-low-byte contract used by `uni2char()`.
- Cross-chunk boundaries are sensitive: this chunk starts after the declaration of `u2c_7A` and ends before `u2c_C6` is complete. Automated merging must not treat these as independent complete tables based only on this chunk.
- `0x00,0x00` is overloaded as the unmapped sentinel. CP949 output byte pairs containing a zero byte would be impossible to represent through this scheme, but CP949 double-byte encodings used here do not require NUL bytes.
- Sparse CJK pages have many unmapped entries; callers must tolerate `-EINVAL` for valid Unicode scalar values that CP949 cannot encode.
- Dense Hangul pages have no zero sentinel entries in the covered `u2c_AC..u2c_C6` portion. Any accidental zero pair introduced there would be a user-visible conversion failure for Korean filenames.

## Cross-Chunk References

- Prior chunk: defines the start of the Unicode-to-CP949 table section and the beginning of `u2c_7A`; this chunk continues `u2c_7A` from offset `0x14`.
- Later chunk: completes `u2c_C6`, continues the dense Hangul tables through later pages, defines `page_uni2charset[]`, case-folding tables, `uni2char()`, `char2uni()`, `struct nls_table table`, and module init/exit registration.
- Earlier file section: `c2u_XX` tables and `page_charset2uni[]` provide the reverse CP949-to-Unicode direction used by `char2uni()`. This chunk is the forward Unicode-to-CP949 counterpart.

## Summary

Lines 8201-12440 are lookup data for forward CP949 encoding. The sparse `u2c_7A..u2c_9F` region maps selected CJK characters and marks unsupported code points with zero pairs; the dense `u2c_AC..u2c_C6` region maps contiguous Hangul syllables to CP949 byte pairs. There is no executable logic here, but the tables are on the critical path for `uni2char()` and must remain byte-count aligned with `page_uni2charset[]`.

### Chunk 4: lines 12441-13947

# Chunk Research: sources/os/linux/linux-stable/fs/nls/nls_cp949.c lines 12441-13947

## Scope

This chunk is the final slice of the Linux NLS CP949/EUC-KR conversion module. It starts inside the tail of a Unicode-to-charset page table from the previous chunk, defines additional Unicode page mapping tables, builds the `page_uni2charset` dispatch table, defines byte-wise case-folding tables, implements both conversion callbacks, and registers the charset as a kernel NLS table.

The file is in subset A through `sources/os/linux/linux-stable`.

## APIs And Data

- Static Unicode-to-charset tables visible here:
  - Tail of the previous `u2c_C6` table at lines 12441-12471.
  - Complete `u2c_C7` through `u2c_D7` tables, each declared as `static const unsigned char ...[512]`, mapping one Unicode high-byte page and 256 low-byte slots to two CP949 output bytes.
  - Sparse/special pages `u2c_DC`, `u2c_F9`, `u2c_FA`, and `u2c_FF`. These include zero pairs for unmapped Unicode positions.
- `page_uni2charset[256]` maps a Unicode high byte to one of the `u2c_*` tables or `NULL`. This is the main dispatch table for `uni2char()`.
- `charset2lower[256]` and `charset2upper[256]` provide single-byte case mapping. Only ASCII letters are folded; bytes `0x80-0xff` map to themselves.
- `uni2char()` is the NLS Unicode-to-CP949 callback.
- `char2uni()` is the CP949-to-Unicode callback and consumes earlier `page_charset2uni` tables.
- `table` registers charset `"cp949"` with alias `"euc-kr"`.

## Control Flow

`uni2char()` validates output space, splits Unicode into high/low bytes, dispatches through `page_uni2charset[ch]`, emits two CP949 bytes when mapped, rejects `0x00,0x00` mappings with `-EINVAL`, or falls back to one-byte identity for nonzero Unicode page 0 values.

`char2uni()` validates input length, maps one-byte input directly, otherwise dispatches first byte through `page_charset2uni`. If a double-byte page and nonzero second byte exist, it reads the Unicode mapping, rejects zero mappings, and returns 2; otherwise it maps the first byte directly.

Module init/exit simply call `register_nls(&table)` and `unregister_nls(&table)`.

## State And Dependencies

All mapping data is `static const`; there is no mutable conversion state beyond the static `struct nls_table` registration. Dependencies include earlier `u2c_*` tables, earlier `page_charset2uni`/`charset2uni` tables, Linux NLS APIs, module macros, and errno values.

## Risks

- Large generated tables can silently encode wrong character mappings.
- `0x00,0x00` is the invalid sentinel for Unicode-to-charset entries.
- Truncated multibyte input can be accepted as one-byte identity if callers pass `boundlen == 1`.
- Case folding is ASCII-only and byte-wise.
- `page_uni2charset` must stay synchronized with all generated table declarations.

## Cross-Chunk References

This chunk starts inside a table opened earlier, relies on earlier chunks for most `u2c_*` pages and all charset-to-Unicode tables, and is the terminal chunk containing conversion callbacks, NLS registration, module hooks, and metadata.

## Verification

- Read `Docs/research_subset_a.md`.
- Read complete requested range `12441-13947`.
- Wrote the chunk report to `Docs/researches/chunks/chunk_sources_os_linux_linux_stable_fs_nls_nls_cp949_c_4_12441_13947_9a944806100b_research.md`.
- Did not create the final per-file report.
