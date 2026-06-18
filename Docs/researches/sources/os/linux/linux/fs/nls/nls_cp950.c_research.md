# File Research: sources/os/linux/linux/fs/nls/nls_cp950.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-4046, source bytes 262089, report `Docs/researches/chunks/chunk_sources_os_linux_linux_fs_nls_nls_cp950_c_1_1_4046_13485365a1c1_research.md`
- chunk 2: lines 4047-8283, source bytes 262112, report `Docs/researches/chunks/chunk_sources_os_linux_linux_fs_nls_nls_cp950_c_2_4047_8283_c5cc4d81441c_research.md`
- chunk 3: lines 8284-9483, source bytes 69713, report `Docs/researches/chunks/chunk_sources_os_linux_linux_fs_nls_nls_cp950_c_3_8284_9483_bb14b2fa077c_research.md`

## Chunk Research

### Chunk 1: lines 1-4046

# Chunk Research: sources/os/linux/linux/fs/nls/nls_cp950.c lines 1-4046

## Scope

This chunk covers the start of Linux's CP950/Big5 NLS module. The visible code is generated conversion data plus the first dispatch table for byte-to-Unicode decoding and the start of reverse Unicode-to-byte data. It does not include the executable conversion callbacks, NLS registration, case tables, or module init/exit definitions; those appear after this chunk.

## APIs And External Interfaces

- Includes at lines 10-14 bring in module metadata, kernel helpers, string declarations, the NLS interface, and errno values.
- No functions or exported symbols are defined in this chunk.
- The file-level external contract is implied by later `struct nls_table` use: these static tables back CP950/Big5 conversion callbacks for the kernel NLS layer.
- The comment identifies the table as automatically generated from Microsoft's codepage data. That matters because most edits should be regeneration/verification work, not hand changes to isolated literals.

## Byte-To-Unicode Tables

- Lines 16-3126 define complete `static const wchar_t c2u_XX[256]` pages for CP950 lead bytes: `A1-AF`, `B0-BF`, `C0-C6`, `C9-CF`, `D0-DF`, `E0-EF`, and `F0-F9`.
- There are no `c2u_C7` or `c2u_C8` tables in this chunk; the dispatch table leaves those lead-byte pages `NULL`.
- Each table is indexed by the second byte of a two-byte CP950 sequence. Unassigned entries are `0x0000`.
- Early pages cover punctuation, fullwidth ASCII, Greek, Bopomofo, math signs, box drawing, Roman numerals, and units. Later pages cover dense Traditional Chinese/CJK mappings plus CP950 extensions.

## Decode Dispatch Table

- Lines 3128-3161 define `page_charset2uni[256]`.
- The populated range starts at `0xA1`, maps `0xA1-0xC6`, skips `0xC7-0xC8`, maps `0xC9-0xF9`, and leaves `0xFA-0xFF` as `NULL`.
- Adjacent later code shows `char2uni()` uses this table, rejects `0x0000` entries, and otherwise consumes two bytes; missing pages fall back to one-byte output.

## Unicode-To-Byte Reverse Tables

- Lines 3163-4046 start `static const unsigned char u2c_XX[512]` reverse pages.
- Complete reverse tables visible here include `u2c_02`, `u2c_03`, `u2c_20`, `u2c_21`, `u2c_22`, `u2c_23`, `u2c_25`, `u2c_26`, `u2c_30` through `u2c_33`, and `u2c_4E` through `u2c_52`.
- `u2c_53` starts at line 3985, but this chunk ends inside it at line 4046. The rest continues in the next chunk.
- Reverse entries are byte pairs; `00 00` is the unmapped sentinel rejected later by `uni2char()`.

## State, Dependencies, And Risks

- All visible data is `static const`, file-local, immutable, and lock-free.
- No allocation, mutable state, module lifecycle code, or executable control flow appears in this chunk.
- Later chunks must provide `page_uni2charset`, case maps, conversion callbacks, `struct nls_table`, module init/exit, and `MODULE_ALIAS_NLS(big5)`.
- Main risks are generated-table corruption, dispatch-table slot misalignment, and incorrect conclusions from this chunk alone because the boundary splits `u2c_53`.

### Chunk 2: lines 4047-8283

# Chunk Research: sources/os/linux/linux/fs/nls/nls_cp950.c lines 4047-8283

## Scope

This chunk is generated-style static lookup data for the Linux NLS CP950/Big5 module. It contains no executable functions, exported symbols, module metadata, or registration code. The line range covers Unicode-to-charset reverse mapping tables:

- The tail of `u2c_53[512]`, beginning at Unicode page `0x53` low-byte entries `0xF0..0xFF`.
- Full `u2c_54[512]` through `u2c_91[512]`.
- Nearly all of `u2c_92[512]`, from entries `0x00..0xFB`; the final `0xFC..0xFF` row and closing brace are just after this chunk.

The data is part of the reverse direction used to encode Unicode code points into CP950 byte pairs.

## APIs And Data Structures

The chunk defines internal `static const unsigned char` table data only. Each `u2c_XX[512]` table represents one Unicode high-byte page `0xXX`, with 256 two-byte CP950 results:

- `0x00, 0x00` is the unmapped sentinel.
- Byte offset `low * 2` is the first CP950 byte.
- Byte offset `low * 2 + 1` is the second CP950 byte.

Adjacent code shows the consumer contract: `uni2char()` indexes `page_uni2charset[ch]`, reads the pair at `cl * 2`, and rejects `{0x00, 0x00}` with `-EINVAL`.

## Control Flow

There is no runtime branch, loop, allocation, locking, or I/O in this chunk. Runtime behavior is table-driven later by `uni2char()`:

1. Split `wchar_t` into high and low bytes.
2. Use the high byte to select one `u2c_*` page.
3. Use the low byte to select a CP950 byte pair.
4. Return two bytes, `-EINVAL`, or `-ENAMETOOLONG`.

## State And Dependencies

All state here is immutable module-local data. Earlier chunks define the file header, forward `c2u_*` tables, `page_charset2uni`, and early reverse pages through most of `u2c_53`. Later code defines `page_uni2charset`, case tables, `uni2char()`, `char2uni()`, `struct nls_table`, and module init/exit.

## Risks And Edge Cases

- A single wrong byte pair silently changes filename transcoding.
- The chunk starts mid-`u2c_53` and ends mid-`u2c_92`, so syntax and table completeness require adjacent chunks.
- Forward and reverse mappings are independent generated tables; this chunk alone cannot prove inversion correctness.
- `uni2char()` only uses the low 16 bits of `wchar_t`, so non-BMP Unicode values are outside this table design.

## Cross-Chunk References

- Previous chunk: earlier reverse pages plus CP950-to-Unicode data used by `char2uni()`.
- Next chunk: completes `u2c_92`, defines later `u2c_*` pages, then the dispatch table and NLS callbacks.
- Final per-file merge should describe this as a generated static NLS mapping module driven by immutable mapping arrays and small conversion callbacks.

### Chunk 3: lines 8284-9483

# Chunk Research: sources/os/linux/linux/fs/nls/nls_cp950.c lines 8284-9483

## Scope

This chunk covers the tail of the generated Unicode-to-CP950 table data and the runtime NLS entry points for the Linux `cp950`/`big5` charset module. It is data-heavy: most of the chunk is static reverse-mapping arrays, followed by the page dispatch table, ASCII-only case-folding tables, conversion callbacks, `struct nls_table`, and module registration metadata.

## APIs And Entry Points

- `uni2char()` implements the NLS Unicode-to-charset callback. It returns output length or `-ENAMETOOLONG`/`-EINVAL`.
- `char2uni()` implements the NLS charset-to-Unicode callback. It returns consumed input length or `-ENAMETOOLONG`/`-EINVAL`.
- `table` publishes `.charset = "cp950"`, `.alias = "big5"`, conversion callbacks, and byte case maps.
- `init_nls_cp950()` / `exit_nls_cp950()` register and unregister the table with the kernel NLS core.
- Module macros provide lifecycle and alias metadata.

## Mapping Data

Lines 8287-9289 define reverse Unicode-page tables `u2c_93` through `u2c_9F`, plus `u2c_DC`, `u2c_F9`, `u2c_FA`, `u2c_FE`, and `u2c_FF`. Each entry stores two CP950 bytes per Unicode low byte; `0x00,0x00` means unmapped.

`page_uni2charset[256]` dispatches Unicode high-byte pages to these and earlier `u2c_*` arrays. `charset2lower` and `charset2upper` are ASCII-only byte case maps; bytes `0x80-0xff` remain identity.

## Control Flow

`uni2char()` splits `wchar_t` into high and low bytes, selects a page via `page_uni2charset`, writes a two-byte CP950 pair, and rejects zero pairs. If Unicode page is zero and low byte is nonzero, it emits a one-byte ASCII value.

`char2uni()` rejects empty input. With one byte available, it returns identity Unicode for that byte. With two bytes, it indexes `page_charset2uni[rawstring[0]]` and then the selected table by `rawstring[1]`; zero Unicode results are invalid. Missing table or zero second byte falls back to one-byte identity.

## State And Dependencies

All tables are `static const`; runtime conversion has no mutable state except module registration. This chunk depends on Linux NLS APIs, module macros, errno values, `wchar_t`, and earlier file definitions, especially `page_charset2uni` and prior `u2c_*` arrays.

## Risks And Edge Cases

- `uni2char()` rejects `U+0000`.
- `char2uni()` treats a single available lead byte as identity rather than incomplete multibyte input.
- Short initializer arrays rely on C zero-fill, intentionally producing unmapped entries.
- Duplicate mappings can make round trips direction-dependent.
- Case folding is byte-wise ASCII-only, not fullwidth or multibyte aware.

## Cross-Chunk References

The chunk begins by closing a table started in the previous chunk. `page_uni2charset` references many earlier reverse tables (`u2c_02`, `u2c_03`, `u2c_20`-`u2c_92`, etc.). `char2uni()` depends on earlier forward `c2u_*` tables through `page_charset2uni`. This chunk completes the file’s runtime module wiring but does not create the merged per-file report.
