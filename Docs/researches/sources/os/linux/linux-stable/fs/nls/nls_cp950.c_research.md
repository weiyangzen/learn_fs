# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp950.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-4046, source bytes 262089, report `Docs/researches/chunks/chunk_sources_os_linux_linux_stable_fs_nls_nls_cp950_c_1_1_4046_0d7e70e6e2f2_research.md`
- chunk 2: lines 4047-8283, source bytes 262112, report `Docs/researches/chunks/chunk_sources_os_linux_linux_stable_fs_nls_nls_cp950_c_2_4047_8283_691da7689f64_research.md`
- chunk 3: lines 8284-9483, source bytes 69713, report `Docs/researches/chunks/chunk_sources_os_linux_linux_stable_fs_nls_nls_cp950_c_3_8284_9483_9ffaf86e2263_research.md`

## Chunk Research

### Chunk 1: lines 1-4046

# Chunk Research: sources/os/linux/linux-stable/fs/nls/nls_cp950.c lines 1-4046

## Scope

This chunk covers the beginning of Linux's generated CP950/Big5 NLS module. It includes the file header, Linux/NLS includes, the complete forward byte-to-Unicode table pages for CP950 lead bytes `0xA1` through `0xF9`, the `page_charset2uni` dispatch table, and the first reverse Unicode-to-charset table pages through most of `u2c_53`. The chunk ends inside `u2c_53`; executable conversion functions and module registration are outside this chunk.

## APIs And Dependencies

- The chunk declares no callable functions. Its public behavior is indirect: later `uni2char`, `char2uni`, and `struct nls_table` code use these static tables to implement the kernel NLS API for the `big5` alias.
- Includes at lines 10-14 pull in kernel module infrastructure, core kernel definitions, string helpers, NLS interfaces, and errno values. In this chunk, the visible dependency is mainly `wchar_t` from Linux NLS/types and `NULL` for dispatch tables.
- All visible data is `static const`, so it has internal linkage and read-only semantics once compiled into the module.

## Forward Charset-To-Unicode State

- `c2u_A1` begins at line 16 and maps CP950 lead byte `0xA1`, indexed by trail byte. It contains punctuation, full-width forms, arrows, box/geometry symbols, and other non-CJK symbols.
- The chunk defines complete `wchar_t c2u_XX[256]` pages for `XX = A1..AF`, `B0..BF`, `C0..C6`, `C9..CF`, `D0..DF`, `E0..EF`, and `F0..F9`.
- `c2u_C7` and `c2u_C8` are absent; `page_charset2uni` maps those lead-byte slots to `NULL`. `FA..FF` are also `NULL`.
- `0x0000` entries represent unmapped byte positions. Valid Big5/CP950 trails mostly appear in `0x40..0x7E` and `0xA1..0xFE`.
- `c2u_F9` includes CP950 extension and box-drawing mappings near the end, including Unicode box-drawing code points around `0x2550..0x2570`.

## Forward Dispatch Table

- `page_charset2uni[256]` at lines 3128-3161 is the first-level lookup table for double-byte decoding.
- Later decoding can read `page_charset2uni[first_byte]`; a `NULL` page is an invalid lead byte, while a non-`NULL` page maps the second byte.
- The `c2u_*` arrays are consumed through this dispatch table.

## Reverse Unicode-To-Charset State

- Reverse mapping begins at `u2c_02[512]` on line 3163. Each table stores two bytes per low-byte Unicode code point. `0x00, 0x00` means unmapped.
- Complete reverse pages visible here include `u2c_02`, `u2c_03`, `u2c_20`, `u2c_21`, `u2c_22`, `u2c_23`, `u2c_25`, `u2c_26`, `u2c_30`, `u2c_31`, `u2c_32`, `u2c_33`, `u2c_4E`, `u2c_4F`, `u2c_50`, `u2c_51`, and `u2c_52`.
- `u2c_53[512]` starts at line 3985 and is only partially inside this chunk. Lines 3985-4046 cover through low-byte comments `0xEC-0xEF`; the remaining `0xF0-0xFF` entries and closing brace continue in the next chunk.

## Control Flow

- There is no runtime control flow in this chunk. It is static table initialization.
- Implied decode flow: later code handles ASCII/single-byte cases, then uses `page_charset2uni[first_byte]`, rejects `NULL`, indexes by second byte, and rejects `0x0000`.
- Implied encode flow: later code uses a Unicode high byte to select `page_uni2charset`, indexes a `u2c_XX` page by low byte, and treats `0x00,0x00` as unmapped.

## Risks And Invariants

- Table generation integrity is the main risk; a misplaced value silently changes filename encoding/decoding behavior for filesystems using this NLS table.
- `0x0000` and `0x00,0x00` are sentinels and must remain distinguishable from valid mappings.
- Forward and reverse tables must remain mutually consistent. Reverse tables encode the chosen canonical CP950 byte sequence for `uni2char`.
- The chunk boundary splits `u2c_53`; merged reporting must treat lines 3985-4051 as one logical table.
- Later conversion functions must enforce unsigned indexing, input length, and page availability.

## Cross-Chunk References

- Lines after 4046 continue and close `u2c_53`, then define more `u2c_*` pages, `page_uni2charset`, case conversion tables, `uni2char`, `char2uni`, the `nls_table`, and module init/exit registration.
- The final per-file report should connect this chunk’s `page_charset2uni` to later `char2uni`, and this chunk’s early `u2c_*` pages to later `page_uni2charset` and `uni2char`.

### Chunk 2: lines 4047-8283

# Chunk Research: sources/os/linux/linux-stable/fs/nls/nls_cp950.c lines 4047-8283

## Scope

This chunk is generated-style static data for Linux's CP950/Big5 NLS module. It contains no functions, module registration, exported symbols, dynamic state, allocation, locking, or I/O. The covered line range is part of the Unicode-to-charset reverse mapping area:

- The tail of `u2c_53[512]`, covering Unicode high byte `0x53` low-byte entries `0xF0..0xFF`.
- Complete reverse pages `u2c_54[512]` through `u2c_91[512]`.
- Nearly all of `u2c_92[512]`, covering entries `0x00..0xFB`; the final `0xFC..0xFF` row and closing brace are in the next chunk.

Each table page maps one 16-bit Unicode high-byte page to CP950 byte pairs for encoding.

## APIs And Data Structures

The chunk defines internal immutable arrays only:

- `static const unsigned char u2c_XX[512]` for Unicode pages `0x53..0x92` in this slice.
- Each page has 256 logical slots, two bytes per low-byte Unicode value.
- Slot `cl` is read at `u2c_XX[cl * 2]` and `u2c_XX[cl * 2 + 1]`.
- `{0x00, 0x00}` is the unmapped sentinel, not a valid CP950 output.

Adjacent context shows these arrays are later wired into `page_uni2charset[256]`, then consumed by `uni2char()`. That callback splits `wchar_t` into high byte `ch` and low byte `cl`, selects `page_uni2charset[ch]`, emits the selected two-byte pair, and rejects `{0x00, 0x00}` with `-EINVAL`.

## Control Flow

There is no runtime control flow in this chunk. Runtime behavior is table-driven by later code:

1. `uni2char()` checks output length.
2. It indexes `page_uni2charset` by Unicode high byte.
3. If a page exists, it reads this chunk's two-byte slot by Unicode low byte.
4. It returns two CP950 bytes or rejects unmapped slots.
5. If no page exists and the high byte is zero, later code falls back to single-byte ASCII handling.

This chunk therefore contributes data to the encode path only. The decode path uses the earlier `c2u_*` and `page_charset2uni` tables, not these `u2c_*` pages directly.

## State And Dependencies

All visible state is `static const`, module-local, and read-only after compilation. The tables depend on the surrounding generated file convention:

- Previous chunk defines the header/includes, CP950-to-Unicode tables, `page_charset2uni`, earlier reverse pages, and the beginning of `u2c_53`.
- This chunk continues the reverse Unicode-to-CP950 table sequence for the main CJK ranges.
- Next chunk completes `u2c_92`, defines later reverse pages, `page_uni2charset`, case-conversion tables, `uni2char()`, `char2uni()`, the `nls_table`, and module init/exit registration.

## Risks And Invariants

- Table integrity is the central risk. A one-byte edit silently changes filename transcoding for filesystems using the `cp950`/`big5` NLS table.
- The endpoint tables are split across chunks: `u2c_53` begins before this chunk and `u2c_92` ends after it. Any syntax or completeness check must merge adjacent chunks.
- The reverse tables must remain consistent with the forward `c2u_*` tables, although duplicate/compatibility mappings may make the reverse direction a generated canonical choice rather than a perfect inverse.
- `{0x00, 0x00}` must remain reserved for unmapped Unicode slots because later `uni2char()` uses that exact pair as the error condition.
- The design is 16-bit-page based. Later code masks `wchar_t` into high/low bytes, so non-BMP code points are outside this table layout.

## Cross-Chunk References

- Previous chunk: lines 3985-4046 contain the start of `u2c_53`; lines 4047-4051 here complete it.
- Next chunk: line 8284 completes `u2c_92`, and later lines build `page_uni2charset` that references every complete `u2c_*` page, including those defined here.
- Final per-file research should connect this chunk's immutable reverse pages to `uni2char()` and contrast them with the earlier forward `char2uni()` tables.

### Chunk 3: lines 8284-9483

# Chunk Research: sources/os/linux/linux-stable/fs/nls/nls_cp950.c lines 8284-9483

## Scope

This chunk covers the tail of the generated Unicode-to-CP950 reverse mapping data and the complete runtime wiring for the Linux `cp950`/`big5` NLS module. Most lines are immutable lookup tables; the executable surface is limited to the two NLS conversion callbacks, table registration, and module metadata at the end of the file.

## APIs And Entry Points

- `uni2char(const wchar_t uni, unsigned char *out, int boundlen)` is the NLS Unicode-to-charset encoder callback. It returns `1` or `2` bytes written, or `-ENAMETOOLONG` / `-EINVAL`.
- `char2uni(const unsigned char *rawstring, int boundlen, wchar_t *uni)` is the NLS charset-to-Unicode decoder callback. It returns `1` or `2` input bytes consumed, or `-ENAMETOOLONG` / `-EINVAL`.
- `table` publishes the kernel `struct nls_table` for `.charset = "cp950"` with `.alias = "big5"`, the two callbacks, and byte case-folding tables.
- `init_nls_cp950()` and `exit_nls_cp950()` call `register_nls(&table)` and `unregister_nls(&table)`.
- `module_init`, `module_exit`, `MODULE_DESCRIPTION`, `MODULE_LICENSE`, and `MODULE_ALIAS_NLS(big5)` expose the module lifecycle and NLS alias.

## Mapping Data

The chunk starts by closing the final row of `u2c_92[512]` from the previous chunk. It then defines `u2c_93` through `u2c_9F`, plus sparse/special pages `u2c_DC`, `u2c_F9`, `u2c_FA`, `u2c_FE`, and `u2c_FF`. These are reverse maps from Unicode high-byte pages to two-byte CP950 sequences; each Unicode low byte selects two adjacent array bytes, and `0x00, 0x00` is the unmapped sentinel.

`page_uni2charset[256]` is the high-byte dispatch table used by `uni2char()`. It references reverse pages defined in this chunk and many pages from earlier chunks, including `u2c_02`, `u2c_03`, `u2c_20`-`u2c_33`, `u2c_4E`-`u2c_9F`, `u2c_DC`, `u2c_F9`, `u2c_FA`, `u2c_FE`, and `u2c_FF`.

`charset2lower[256]` and `charset2upper[256]` are byte-level case maps. They fold ASCII letters only; bytes `0x80`-`0xff` remain identity, so CP950 multibyte data is not case-normalized.

## Control Flow

`uni2char()` splits the 16-bit `wchar_t` value into `ch = high byte` and `cl = low byte`. It first rejects `boundlen <= 0`. If `page_uni2charset[ch]` exists, it requires room for two output bytes, copies the pair at `cl * 2`, rejects the all-zero sentinel with `-EINVAL`, and returns `2`. If no reverse page exists and the Unicode high byte is zero with a nonzero low byte, it emits that low byte as a single-byte ASCII-compatible character and returns `1`. All other inputs return `-EINVAL`.

`char2uni()` rejects empty input, decodes a single available byte as identity Unicode, and otherwise reads two bytes. It selects `page_charset2uni[rawstring[0]]`, a forward map defined earlier in the file. If a table exists and the second byte is nonzero, it returns the table entry unless that entry is `0x0000`, which is invalid. Missing table or zero second byte falls back to one-byte identity for the first byte.

Module control flow is direct: init registers the static table with the NLS core; exit unregisters the same table.

## State And Dependencies

All conversion data in this chunk is `static const`; there is no mutable per-call state, allocation, locking, I/O, or reference counting in the callbacks. The only global runtime state change is registration of `table` with the Linux NLS core.

The chunk depends on earlier file definitions for `page_charset2uni` and many `u2c_*` pages referenced by `page_uni2charset`. It also depends on Linux headers for `struct nls_table`, `register_nls`, `unregister_nls`, module macros, `wchar_t`, and errno values.

## Risks And Edge Cases

- Table correctness is the main risk: a wrong byte pair silently changes filename transcoding.
- `uni2char()` rejects `U+0000` because the one-byte fallback requires `cl` to be nonzero and reverse-table zero pairs mean unmapped.
- `char2uni()` treats a single available lead byte as an identity character rather than reporting an incomplete multibyte sequence.
- `char2uni()` also falls back to one-byte identity when the first byte has no CP950 page table or the second byte is zero.
- Short initializer arrays such as `u2c_DC` rely on C zero-fill to mark the rest of the page unmapped.
- Forward and reverse tables are generated independently enough that duplicate or compatibility mappings may not round-trip uniquely.
- Conversion only uses the low 16 bits of `wchar_t`; non-BMP Unicode code points are outside this table design.

## Cross-Chunk References

- Previous chunk: supplies most of `u2c_92` and earlier reverse pages consumed by `page_uni2charset`.
- Earlier chunks: define CP950-to-Unicode `c2u_*` tables and `page_charset2uni`, which `char2uni()` requires.
- This chunk completes the file by adding the final reverse pages, dispatch/case tables, conversion callbacks, and module registration. The final per-file report should merge these findings with the earlier generated table coverage; this chunk intentionally does not create that merged report.
