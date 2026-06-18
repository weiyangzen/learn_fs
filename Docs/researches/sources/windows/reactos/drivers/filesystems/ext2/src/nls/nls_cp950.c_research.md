# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp950.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-3890, source bytes 262080, report `Docs/researches/chunks/chunk_sources_windows_reactos_drivers_filesystems_ext2_src_nls_nls_cp950_c_1_1_dbce4f288dcb_research.md`
- chunk 2: lines 3891-7950, source bytes 262117, report `Docs/researches/chunks/chunk_sources_windows_reactos_drivers_filesystems_ext2_src_nls_nls_cp950_c_2_3_d18642326932_research.md`
- chunk 3: lines 7951-9487, source bytes 94691, report `Docs/researches/chunks/chunk_sources_windows_reactos_drivers_filesystems_ext2_src_nls_nls_cp950_c_3_7_23d36c75e314_research.md`

## Chunk Research

### Chunk 1: lines 1-3890

# Chunk Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp950.c lines 1-3890

## Scope

This chunk covers the opening 1-3890 lines of ReactOS ext2's Linux-style NLS module for CP950/Big5 filename character conversion. The file is generated table code originally identified as `linux/fs/nls_cp950.c`; this chunk contains module includes, all byte-to-Unicode CP950 lead-byte pages, the byte-to-Unicode page index, and the beginning of Unicode-to-CP950 reverse pages. The executable converter functions and module registration are outside this chunk, but adjacent context shows these tables are consumed by `char2uni()`, `uni2char()`, and the `nls_table` registration later in the same file.

## APIs And Entry Points

No callable API is defined inside this chunk. The chunk defines private static data for the later Linux NLS callbacks:

- `static wchar_t c2u_XX[256]` tables map a CP950/Big5 two-byte character with first byte `0xXX` and second byte used as an array index to a Unicode `wchar_t`.
- `static wchar_t *page_charset2uni[256]` maps each possible first byte to the corresponding `c2u_XX` table or `NULL`.
- `static unsigned char u2c_XX[512]` tables map Unicode pages to encoded CP950 bytes, storing two bytes per low-byte Unicode index.

Adjacent context at lines 9401-9461 shows the table API contract:

- `char2uni(rawstring, boundlen, uni)` reads `page_charset2uni[ch]`, indexes by `cl`, rejects `0x0000`, and otherwise falls back to one-byte ASCII-style output when no lead-byte table exists.
- `uni2char(uni, out, boundlen)` reads `page_uni2charset[ch]`, indexes `cl * 2`, rejects an all-zero two-byte pair, and otherwise falls back to one-byte values for Unicode page zero.

## Data Definitions

The file includes Linux kernel/NLS headers at lines 10-14: `linux/module.h`, `linux/kernel.h`, `linux/string.h`, `linux/nls.h`, and `linux/errno.h`.

The forward CP950-to-Unicode tables span lines 16-3129:

- Defined lead-byte pages: `A1` through `C6`, `C9` through `F9`.
- Omitted lead-byte pages visible in this chunk: `C7`, `C8`, and `FA` through `FF` are left unmapped by `page_charset2uni`.
- Every full forward page is a 256-entry `wchar_t` array. Most pages reserve non-trail-byte slots with `0x0000`.
- `c2u_C6` is a shorter initialized array than surrounding pages; because it has explicit `[256]` size, remaining entries are implicitly zero.

The lead-byte dispatch table `page_charset2uni[256]` spans lines 3131-3164 and maps `0xA1-0xC6`, `0xC9-0xF9` to table pointers, with `0xC7`, `0xC8`, and `0xFA-0xFF` as `NULL`.

The reverse Unicode-to-CP950 tables begin at line 3166 and continue past the chunk boundary. This chunk includes `u2c_02`, `u2c_03`, `u2c_20`, `u2c_21`, `u2c_22`, `u2c_23`, `u2c_25`, `u2c_26`, `u2c_30`, `u2c_31`, `u2c_32`, `u2c_33`, `u2c_4E`, `u2c_4F`, `u2c_50`, and the start of `u2c_51`. The chunk ends in the middle of `u2c_51`.

## Control Flow

There is no runtime branch or loop in this chunk. Control flow is encoded as data-driven dispatch for later callbacks:

1. CP950-to-Unicode decoding reads first byte `ch`.
2. `page_charset2uni[ch]` selects a page table only for recognized two-byte lead bytes.
3. The second byte `cl` indexes the selected page.
4. A zero result marks an invalid byte pair.
5. If no page exists for `ch`, adjacent `char2uni()` treats the byte as a single-byte character.

The reverse direction uses Unicode high byte to select `page_uni2charset[ch]`, then low byte to index a two-byte pair in `u2c_XX`.

## State And Mutability

All data in this chunk is file-scope `static` storage. None is declared `const`, even though the tables are intended to be immutable after module load. Later conversion callbacks read these arrays but do not modify them.

## Dependencies

This chunk depends on the Linux NLS/module compatibility environment used by the ReactOS ext2 driver:

- `wchar_t` and `NULL`
- `struct nls_table`, `register_nls()`, `unregister_nls()`, `THIS_MODULE`, `module_init()`
- errno values such as `-EINVAL` and `-ENAMETOOLONG`

The data is generated from Microsoft CP950 Unicode mapping data according to the file header.

## Risks And Edge Cases

- Invalid two-byte sequences are represented by `0x0000` in forward tables and `0x00, 0x00` in reverse tables.
- Unicode NUL is not encodable through the two-byte path; adjacent `uni2char()` also requires page-zero `cl` to be nonzero.
- Adjacent `char2uni()` returns a single-byte character whenever `page_charset2uni[ch]` is `NULL`, which may be permissive for malformed CP950 byte streams.
- Adjacent `char2uni()` treats `boundlen == 1` as a one-byte character, so a dangling CP950 lead byte decodes as that byte.
- Tables are writable static data because they are not `const`.
- The chunk boundary interrupts `u2c_51`; reverse-map coverage must be continued in later chunks.

## Cross-Chunk References

- Later chunk completes `u2c_51`, defines the rest of the `u2c_XX` reverse tables, `page_uni2charset[256]`, `charset2lower[256]`, and `charset2upper[256]`.
- Later chunk defines `uni2char()` and `char2uni()`, the actual NLS callbacks consuming these tables.
- Later chunk defines the `nls_table` for charset `"cp950"` and alias `"big5"`, plus module init/exit registration.

### Chunk 2: lines 3891-7950

# Chunk Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp950.c lines 3891-7950

## Scope

This chunk is the middle of ReactOS ext2's generated CP950/Big5 NLS conversion source. It contains only static Unicode-to-charset lookup data, plus the tail of the previous table and the declaration line for the next table. It does not define exported APIs, driver entry points, locking, allocation, I/O, or filesystem metadata logic.

The active data in this range is part of `page_uni2charset[]`'s backing table set used later by `uni2char()`. Each `u2c_XX` table maps Unicode code points with high byte `0xXX` to two CP950 bytes. A pair of `0x00, 0x00` means unmappable.

## APIs And Entry Points

- No functions or public APIs are declared in this chunk.
- The chunk contributes `static unsigned char u2c_XX[512]` arrays, which are private translation tables for the file-local NLS implementation.
- Adjacent lookup code outside this chunk wires these arrays into `page_uni2charset[256]` and exposes them through the file's `static struct nls_table table` callbacks:
  - `uni2char()` for Unicode to CP950 conversion.
  - `char2uni()` for CP950 to Unicode conversion, using separate `c2u_*` tables from earlier chunks.
  - module registration through `register_nls(&table)` and alias `big5`.

## Data Covered

The chunk starts at line 3891 inside the prior `u2c_51` table and includes its final entries before `u2c_52` begins at line 3920. It then contains these complete or visible table declarations:

- Complete in this chunk: `u2c_52` through `u2c_8D`.
- Starts at the final line of this chunk: `u2c_8E`.
- Partial before this chunk: `u2c_51`.

The complete tables correspond to Unicode high-byte pages `0x52xx` through `0x8Dxx`, mostly CJK mapping ranges. Several arrays have fewer explicit initializers than their 512-byte capacity; C zero-fills the remaining bytes, preserving the unmappable `0x00, 0x00` sentinel behavior.

## Control Flow

There is no direct control flow in lines 3891-7950. Runtime use is later:

1. `uni2char()` splits `wchar_t uni` into high byte `ch` and low byte `cl`.
2. It selects `page_uni2charset[ch]`.
3. For pages in this chunk, entries `0x52` through `0x8D` point to the corresponding `u2c_*` tables.
4. It reads two bytes at `cl * 2`.
5. `0x00, 0x00` returns `-EINVAL`; otherwise the conversion emits two CP950 bytes.

## State, Dependencies, Risks

All data here has internal linkage through `static`, but the arrays are not `const`, so they occupy writable static storage despite being lookup data. There is no locking, allocation, or mutable runtime state in this chunk.

Dependencies are structural: these arrays rely on the generated two-byte-per-entry layout, `page_uni2charset[]`, and `uni2char()`'s zero-pair invalid-marker contract. Risks are table corruption, malformed regeneration, or chunk-boundary misunderstanding around partial `u2c_51` and `u2c_8E`.

## Cross-Chunk References

- Previous chunk contains the start of `u2c_51`, earlier `u2c_*` tables, the reverse `c2u_*` tables, and `page_charset2uni[]`.
- This chunk completes the visible tail of `u2c_51`, defines `u2c_52` through `u2c_8D`, and starts `u2c_8E`.
- Next chunk continues `u2c_8E`, defines later `u2c_*` pages, and contains `page_uni2charset[]`, case tables, conversion functions, and NLS registration.

### Chunk 3: lines 7951-9487

# Chunk Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp950.c lines 7951-9487

## Scope

This chunk covers the tail of the generated ReactOS ext2 NLS table for CP950/Big5. It begins one line after the declaration of `u2c_8E`, finishes the remaining Unicode-to-charset lookup pages, builds the `page_uni2charset` dispatch table, defines byte-case folding tables, implements the `uni2char` and `char2uni` conversion callbacks, and registers the `cp950` NLS module aliasing `big5`.

The opening line range is inside `u2c_8E`; the table declaration starts at line 7950, just before this chunk. Earlier chunks define the includes, the reverse `c2u_*` charset-to-Unicode pages, `page_charset2uni`, and Unicode-to-charset pages up through `u2c_8D`.

## APIs And Entry Points

- `uni2char(const wchar_t uni, unsigned char *out, int boundlen)` converts one Unicode code point to CP950/Big5 bytes for the NLS table.
- `char2uni(const unsigned char *rawstring, int boundlen, wchar_t *uni)` converts one CP950/Big5 byte sequence to a Unicode `wchar_t`.
- `init_nls_cp950()` registers the local `struct nls_table table` with `register_nls()`.
- `exit_nls_cp950()` unregisters the same table with `unregister_nls()`.
- `module_init(init_nls_cp950)`, `module_exit(exit_nls_cp950)`, `MODULE_LICENSE("Dual BSD/GPL")`, and `MODULE_ALIAS_NLS(big5)` expose this file as a loadable NLS module.

## Data Tables

The first major block is generated static mapping data:

- `u2c_8E` through `u2c_9F` map Unicode pages `0x8E00` through `0x9FFF` to two-byte CP950/Big5 sequences, using `{0x00, 0x00}` as unmapped sentinels.
- `u2c_DC` is a sparse page with only zero entries in this chunk.
- `u2c_F9` and `u2c_FA` cover compatibility/private mapping ranges used by CP950.
- `u2c_FE` and `u2c_FF` cover fullwidth/symbol ranges, including punctuation, fullwidth digits/letters, and related Big5 symbol-zone mappings.
- `page_uni2charset[256]` maps the high byte of a Unicode value to the corresponding `u2c_*` page pointer. NULL high-byte entries are treated as unsupported pages, except low ASCII handled separately by `uni2char()`.
- `charset2lower[256]` and `charset2upper[256]` perform single-byte ASCII-only case folding: `A-Z` lower to `a-z`, `a-z` upper to `A-Z`, and all non-ASCII bytes remain unchanged.

The tables are mutable only because they are declared as `static unsigned char` rather than `static const`; this chunk does not write to them.

## Control Flow

`uni2char()` first rejects a non-positive output bound with `-ENAMETOOLONG`. It splits `uni` into low byte `cl` and high byte `ch`, indexes `page_uni2charset[ch]`, and if a page exists requires at least two output bytes. It copies the two bytes at `cl * 2` and `cl * 2 + 1`, rejects the `{0,0}` sentinel with `-EINVAL`, and returns `2`. If no page exists but `ch == 0 && cl` is true, it emits the low byte directly as one-byte ASCII and returns `1`. All other Unicode values return `-EINVAL`.

`char2uni()` first rejects a non-positive input bound with `-ENAMETOOLONG`. If only one input byte is available, it treats that byte as a complete single-byte character, stores it directly in `*uni`, and returns `1`. With at least two bytes available, it reads lead byte `ch` and trail byte `cl`, looks up `page_charset2uni[ch]` from the earlier chunk, and if a page exists and `cl` is nonzero, returns `charset2uni[cl]` unless that entry is `0x0000`, in which case it returns `-EINVAL`. If there is no page for the lead byte or the second byte is zero, it falls back to treating the lead byte as a one-byte character and returns `1`.

The module registration flow is minimal: the static `table` binds charset name `cp950`, alias `big5`, the two conversion callbacks, the case-fold tables, and `THIS_MODULE`; init registers it and exit unregisters it.

## State And Dependencies

The important local state is table-driven and process-global: all `u2c_*` arrays, `page_uni2charset`, `charset2lower`, `charset2upper`, and the final `struct nls_table table`.

This chunk depends on earlier file definitions for `page_charset2uni` and the `c2u_*` charset-to-Unicode arrays used by `char2uni()`. It also depends on kernel/ReactOS NLS infrastructure types and symbols visible from the file header, including `wchar_t`, `struct nls_table`, `THIS_MODULE`, `register_nls()`, `unregister_nls()`, `module_init`, `module_exit`, `MODULE_LICENSE`, `MODULE_ALIAS_NLS`, and errno constants `ENAMETOOLONG` and `EINVAL`.

There is no dynamic allocation, locking, filesystem I/O, or mutable conversion state in this chunk. Conversion behavior is deterministic for one code point or one byte sequence at a time.

## Risks And Edge Cases

- The chunk starts inside `u2c_8E`; its declaration is just outside the range at line 7950, so any table-boundary audit must include that adjacent line.
- Several `u2c_*` arrays are declared as `[512]` but are sparsely initialized or shorter than a full 512-byte literal block. C zero-initialization fills the remainder; conversion correctness relies on `{0,0}` continuing to mean unmapped.
- `char2uni()` treats any single available byte as a valid single-byte Unicode value. For truncated double-byte CP950 input, the callback cannot distinguish truncation from intended single-byte data and returns success with the lead byte.
- `char2uni()` also falls back to one-byte output when the second byte is `0x00` or when no lead-byte page exists, rather than returning `-EINVAL`.
- `uni2char()` only allows direct one-byte output for `ch == 0 && cl`, so Unicode NUL (`U+0000`) is rejected rather than encoded as byte zero.
- Case folding is ASCII-only. Multibyte CP950 letters and any locale-specific mappings are identity mappings in `charset2lower`/`charset2upper`.
- The static lookup tables are not `const`; accidental writes elsewhere in this compilation unit would corrupt global conversion behavior, although this file does not write them.

## Cross-Chunk References

- Earlier chunks define the file header/includes, licensing preamble, and `page_charset2uni`; `char2uni()` cannot be understood independently of those tables.
- Earlier Unicode-to-charset pages `u2c_02` through `u2c_8D` are referenced by `page_uni2charset` in this chunk, so this chunk completes the dispatch table for data declared across the whole file.
- The final `struct nls_table table` is the integration point for the entire file: all generated tables from previous chunks feed the two callbacks registered here.

## Summary

This chunk is the executable tail of an otherwise generated CP950/Big5 NLS mapping file. It finishes the Unicode-to-charset data, wires the high-byte page dispatch table, provides ASCII-only case conversion, implements bounded one-character encode/decode callbacks, and registers the mapping with the ReactOS/Linux-style NLS module system.
