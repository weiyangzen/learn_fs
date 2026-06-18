# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp949.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-3837, source bytes 262134, report `Docs/researches/chunks/chunk_sources_windows_reactos_drivers_filesystems_ext2_src_nls_nls_cp949_c_1_1_64130ec38081_research.md`
- chunk 2: lines 3838-7873, source bytes 262116, report `Docs/researches/chunks/chunk_sources_windows_reactos_drivers_filesystems_ext2_src_nls_nls_cp949_c_2_3_184ad159651f_research.md`
- chunk 3: lines 7874-11936, source bytes 262091, report `Docs/researches/chunks/chunk_sources_windows_reactos_drivers_filesystems_ext2_src_nls_nls_cp949_c_3_7_16b7f548a926_research.md`
- chunk 4: lines 11937-13948, source bytes 125560, report `Docs/researches/chunks/chunk_sources_windows_reactos_drivers_filesystems_ext2_src_nls_nls_cp949_c_4_1_58943dadd792_research.md`

## Chunk Research

### Chunk 1: lines 1-3837

# Chunk Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp949.c lines 1-3837

## Scope

This chunk covers the opening 3,837 lines of the generated ReactOS Ext2 NLS source for code page 949. The file belongs to `sources/windows/reactos`, which is included by `Docs/research_subset_a.md`.

The visible range contains the provenance comment, Linux NLS includes, and the first large byte-to-Unicode lookup-table block for CP949/EUC-KR-compatible multibyte decoding. It starts at `static wchar_t c2u_81[256]` and runs through the beginning of `static wchar_t c2u_ED[256]`; the chunk ends inside `c2u_ED` after the `0x60-0x67` row.

## APIs and Entry Points

- No callable function or exported symbol is defined in this chunk.
- The chunk declares static lookup pages `c2u_81` through `c2u_ED`, one page per possible first byte / lead byte in the CP949 byte stream.
- These arrays are consumed later by `page_charset2uni[256]`, outside this chunk, which dispatches `rawstring[0]` to the matching `c2u_*` page.
- Later code outside this range wires the table data into Linux-style NLS callbacks `char2uni` and `uni2char`, then registers `struct nls_table table` with charset `"cp949"` and alias `"euc-kr"`.

## Control Flow

There is no local control flow in this range. Runtime behavior is table-driven:

- A later decoder checks input length and reads `rawstring[0]` as the lead byte.
- If `page_charset2uni[lead]` is non-`NULL` and the second byte is nonzero, the second byte indexes directly into one of these 256-entry `wchar_t` pages.
- A nonzero table entry is returned as the Unicode value and consumes two bytes.
- A `0x0000` table entry is rejected by the later decoder as an invalid/unmapped double-byte sequence.
- If no page exists for the lead byte, later code falls back to a one-byte identity mapping.

## State and Data Flow

- The chunk stores generated mapping state as file-local `static wchar_t` arrays. They are lookup-only in practice but are not declared `const`.
- Complete regular Hangul-extension pages `c2u_81` through `c2u_A1` each provide 256 initializer values, with 178 nonzero mappings per page. Their populated ranges mostly begin after invalid low-byte slots and map into Hangul syllables from `U+AC02` through `U+C90E`.
- Symbol and compatibility pages `c2u_A2` through `c2u_AF` are more irregular and sparse. Visible mappings include punctuation, arrows, mathematical symbols, fullwidth ASCII, halfwidth Hangul jamo, Roman numerals, Greek, box drawing, circled numbers, hiragana, katakana, Cyrillic, and enclosed CJK/unit symbols.
- Hangul pages `c2u_B0` through `c2u_C8` continue generated syllable mappings from roughly `U+CE9A` through `U+D79D`.
- There is no `c2u_C9` page in this file; later dispatch leaves lead byte `0xC9` as `NULL`.
- CJK/hanja extension pages `c2u_CA` through `c2u_EC` each contain 94 nonzero mappings, mostly in low-byte positions `0xA1-0xFE`.
- The chunk starts `c2u_ED` at line 3824 but only includes its first 104 zero initializer values through low-byte `0x67`.

## Dependencies

- Includes `<linux/module.h>`, `<linux/kernel.h>`, `<linux/string.h>`, `<linux/nls.h>`, and `<linux/errno.h>`.
- Depends on `wchar_t`, Linux errno constants, module metadata macros, and the NLS `struct nls_table` ABI.
- Depends on later local declarations of `page_charset2uni`, reverse `u2c_*` tables, `page_uni2charset`, byte case maps, `char2uni`, `uni2char`, and module init/exit registration.
- The opening comment identifies the table as automatically generated from Microsoft Unicode code page data.

## Risks and Edge Cases

- The lookup arrays are not `const`, so they may occupy writable storage despite being immutable lookup data.
- Sparse pages rely on `0x0000` sentinels and C zero-initialization; regeneration must preserve unmapped slots.
- The chunk boundary splits `c2u_ED`, so merge errors around line 3837 can break compilation or corrupt lead byte `0xED`.
- Mapping correctness is filesystem-visible: wrong conversion can cause failed lookups, filename aliasing, inconsistent case behavior, or broken round trips.
- Tables do no bounds checking; safety depends on later code using `unsigned char` indexes and checking input length.

## Cross-Chunk References

- The next chunk continues and closes `c2u_ED`, then defines remaining forward pages `c2u_EE` through `c2u_FD`.
- Later `page_charset2uni[256]` maps lead bytes `0x81-0xFD` to these pages, with `NULL` holes such as `0xC9`, `0xFE`, and `0xFF`.
- Later reverse tables `u2c_*` and `page_uni2charset[256]` implement Unicode-to-CP949 conversion.
- Later `charset2lower` and `charset2upper` provide byte-level case conversion.
- Final runtime wiring appears near the end of the file in `uni2char`, `char2uni`, `init_nls_cp949`, `exit_nls_cp949`, `module_init`, `module_exit`, and `MODULE_ALIAS_NLS(euc-kr)`.

### Chunk 2: lines 3838-7873

# Chunk Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp949.c lines 3838-7873

## Scope

This chunk is the middle data section of the generated CP949/UHC NLS conversion table used by the ReactOS ext2 filesystem driver copy of a Linux NLS module. It is in subset A because `sources/windows/reactos` is included by `Docs/research_subset_a.md`.

The span contains static lookup data only. It starts inside `c2u_ED[256]`, completes the remaining high CP949 byte-to-Unicode pages through `c2u_FD[256]`, defines the byte-to-Unicode dispatch table, then defines Unicode-to-CP949 reverse lookup pages from `u2c_01[512]` through `u2c_74[512]` plus the beginning of `u2c_75[512]`.

## APIs And Data Structures

- No public API, exported symbol, callback, or module registration function is declared in this chunk.
- The visible data is file-local static storage consumed by later NLS callbacks:
  - `char2uni()` uses `page_charset2uni[ch]` to map a CP949 lead byte plus trail byte into a `wchar_t`.
  - `uni2char()` uses `page_uni2charset[ch]` to map a Unicode high byte to a 512-byte reverse page and emit a two-byte CP949 sequence.
- `c2u_ED[256]` is partially visible from line 3838 to its close at line 3858. The chunk then fully defines `c2u_EE[256]` through `c2u_FD[256]`.
- `page_charset2uni[256]` is the first-level decoder index. It maps lead bytes `0x81..0xC8`, skips `0xC9`, maps `0xCA..0xFD`, and leaves other lead bytes as `NULL`.
- Complete reverse pages in this chunk include `u2c_01`, `u2c_02`, `u2c_03`, `u2c_04`, `u2c_11`, `u2c_20` through `u2c_26`, `u2c_30` through `u2c_33`, and `u2c_4E` through `u2c_74`. The chunk ends after the first entries of `u2c_75`.

## Control Flow

There is no executable control flow in this line range: no functions, branches, loops, locking, allocation, or I/O.

Runtime behavior is table-driven by code outside this chunk: `char2uni()` selects `page_charset2uni[first]` and rejects `0x0000` slots; `uni2char()` selects `page_uni2charset[high]` and rejects `{0x00, 0x00}` pairs.

## State And Dependencies

All visible state is immutable static lookup data with internal linkage. There is no per-volume, per-file, or per-call mutable state in this chunk.

`page_charset2uni[]` depends on `c2u_81` through `c2u_EC` from the previous chunk and on `c2u_ED` through `c2u_FD` at this chunk boundary. The `u2c_*` reverse pages depend on a later `page_uni2charset[]` dispatch table to become reachable from `uni2char()`.

## Risks And Edge Cases

- The arrays are positional generated data. Any inserted, deleted, or reordered literal silently changes filename encoding behavior for CP949-mounted ext2 paths.
- Chunk boundaries split declarations: `c2u_ED[256]` starts before this range, and `u2c_75[512]` continues after it.
- Sentinel zeros are semantically meaningful: `0x0000` rejects a two-byte input sequence; `{0x00, 0x00}` rejects a Unicode-to-CP949 mapping.
- The `page_charset2uni[]` omission of `0xC9`, `0xFE`, and `0xFF` appears deliberate.
- CP949 includes UHC and compatibility mappings, including `U+F9xx` and `U+FAxx` values.

## Cross-Chunk References

- The previous chunk defines the file prologue, earlier `c2u_81` through most of `c2u_ED`, and generated-table context.
- This chunk defines `page_charset2uni[]`, which references byte-to-Unicode pages from both the previous chunk and this chunk.
- The next chunk completes `u2c_75`, defines remaining reverse pages, builds `page_uni2charset[]`, adds case conversion tables, and defines `uni2char()`, `char2uni()`, the `struct nls_table`, init/exit registration, and module metadata.
- This report is only for chunk 2 and intentionally does not create or merge the final per-file report.

### Chunk 3: lines 7874-11936

# Chunk Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp949.c lines 7874-11936

## Scope

This report covers only `sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp949.c` lines 7874-11936 in learn_fs subset A (`Docs/research_subset_a.md`). I read the requested range completely and used adjacent context only to identify enclosing declarations and the later lookup dispatch/consumer functions. The chunk is generated/static CP949 Unicode-to-charset lookup data, not filesystem control logic.

## APIs And Data

This chunk contributes file-local `static unsigned char u2c_*[512]` tables used by the NLS `uni2char` path:

- Starts inside `u2c_75`, covering entries for low-byte offsets `0x34-0xFF`; the declaration begins before this chunk at line 7860.
- Fully defines pages `u2c_76` through `u2c_BE`, with sparse and dense 512-byte mapping arrays.
- Starts `u2c_BF` at line 11929 and covers entries through low-byte offsets `0x18-0x1B`; the rest continues in the next chunk.

Each table represents one Unicode high-byte page. A Unicode code point `0xHHLL` maps through `u2c_HH[LL * 2]` and `u2c_HH[LL * 2 + 1]` to a two-byte CP949 sequence. `0x00, 0x00` marks an unmapped code point.

## Control Flow

There are no functions, loops, conditionals, calls, allocation, locking, or I/O in this chunk. Runtime behavior is indirect: later `uni2char()` indexes `page_uni2charset[ch]`, then reads the two-byte pair from the selected `u2c_*` table, returning `-EINVAL` when the pair is all zero and `-ENAMETOOLONG` when the caller's output buffer cannot hold the result.

## State And Dependencies

The data is static internal translation state for the ReactOS ext2 NLS table named `cp949`. It is consumed by `page_uni2charset[256]` later in the same file, which references this chunk's pages `u2c_75` through `u2c_BF`. The exported NLS surface is the later `struct nls_table table`, whose `.uni2char` callback depends on these arrays.

Several arrays in this generated section are sparse and rely on C zero-initialization for omitted trailing entries. The dense Hangul pages beginning at `u2c_AC` contain many nonzero CP949 pairs, including both standard KS X 1001-style `0xB0..0xBB` byte ranges and CP949 extension byte ranges such as `0x81..0x96`.

## Risks

The primary risk is silent filename conversion error: a single wrong byte pair maps a Unicode character to the wrong CP949 sequence, while a stray `0x00, 0x00` makes a valid character unencodable. Because this data participates in filename NLS conversion, such errors can cause lookup mismatches, inaccessible names, or non-round-tripping directory entries rather than obvious control-flow failures.

The table shape is also fragile. Every page must remain exactly 512 addressable bytes because `uni2char()` indexes by `cl * 2` without per-page bounds checks. File-scope zero-fill makes short initializers safe, but moving these tables to automatic storage or generated binary blobs would need explicit padding.

## Cross-Chunk References

Previous chunks define earlier `u2c_*` pages and the beginning of `u2c_75`; this chunk finishes `u2c_75`. The next chunk continues `u2c_BF` and later pages through the final `page_uni2charset` pointer table. The later dispatch table at lines 13755-13788 references all pages from this chunk, and `uni2char()` at lines 13862-13890 is the direct consumer.

### Chunk 4: lines 11937-13948

# Chunk Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp949.c lines 11937-13948

## Scope

This chunk covers the tail of the CP949 Unicode-to-charset mapping data and the only executable conversion/registration logic visible in the file tail. It starts mid-definition inside `u2c_BF` at Unicode page `0xBF` offset `0x1C`, then defines `u2c_C0` through `u2c_D7`, sparse pages `u2c_DC`, `u2c_F9`, `u2c_FA`, and `u2c_FF`, builds `page_uni2charset[256]`, provides ASCII-only case maps, implements `uni2char()` and `char2uni()`, and registers the `cp949`/`euc-kr` NLS table as a kernel module.

## APIs and Entry Points

- `uni2char()` converts one Unicode code point to one or two CP949 bytes using `page_uni2charset`.
- `char2uni()` converts one CP949 byte sequence to one Unicode code point using `page_charset2uni`.
- `table` exposes charset `"cp949"` with alias `"euc-kr"` to the kernel NLS layer.
- `init_nls_cp949()` and `exit_nls_cp949()` register/unregister the table via `register_nls()` and `unregister_nls()`.

## Control Flow and State

`uni2char()` checks output capacity, splits Unicode into high/low bytes, uses a high-byte page lookup, emits two bytes for mapped pages, rejects zero-pair mappings as `-EINVAL`, and falls back to nonzero ASCII only when no page exists.

`char2uni()` checks input length, treats one-byte input as a single character, otherwise uses the first byte as a lead-byte page selector and the second byte as an index. Missing pages or `cl == 0` fall back to single-byte output.

State is static lookup data plus a static `nls_table`. The arrays are mutable by declaration but used as immutable generated tables.

## Dependencies

This chunk depends on earlier file chunks for `page_charset2uni`, `c2u_*`, and many earlier `u2c_*` pages. It also depends on kernel/NLS types and macros: `wchar_t`, `struct nls_table`, `ENAMETOOLONG`, `EINVAL`, `THIS_MODULE`, `__init`, `__exit`, module macros, and NLS registration APIs.

## Risks and Cross-Chunk Notes

- The chunk begins inside `u2c_BF`; previous chunk data is required for the full page.
- Sparse pages rely on implicit zero fill and zero-pair invalidation.
- Dangling CP949 lead bytes with `boundlen == 1` pass through as single-byte Unicode.
- Case folding is ASCII-only.
- The positional table layout is the contract, so hand edits or formatter rewrites are high risk.
