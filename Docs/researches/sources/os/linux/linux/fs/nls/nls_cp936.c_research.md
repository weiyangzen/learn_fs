# File Research: sources/os/linux/linux/fs/nls/nls_cp936.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-3984, source bytes 262088, report `Docs/researches/chunks/chunk_sources_os_linux_linux_fs_nls_nls_cp936_c_1_1_3984_6153d81b2f92_research.md`
- chunk 2: lines 3985-8212, source bytes 262119, report `Docs/researches/chunks/chunk_sources_os_linux_linux_fs_nls_nls_cp936_c_2_3985_8212_d83329ae5427_research.md`
- chunk 3: lines 8213-11112, source bytes 174159, report `Docs/researches/chunks/chunk_sources_os_linux_linux_fs_nls_nls_cp936_c_3_8213_11112_8039314df632_research.md`

## Chunk Research

### Chunk 1: lines 1-3984

# Chunk Research: sources/os/linux/linux/fs/nls/nls_cp936.c lines 1-3984

## Scope

This chunk covers the beginning of Linux's CP936/GB2312 NLS module source. The visible code is almost entirely generated static decode data: byte-pair lead-byte tables named `c2u_XX` that map CP936 second bytes to Unicode `wchar_t` values. The chunk starts with module/kernel/NLS includes and ends in the middle of `c2u_F1`, so this report intentionally does not describe the complete file implementation as a standalone unit.

## APIs And External Interfaces

- Includes: `linux/module.h`, `linux/kernel.h`, `linux/string.h`, `linux/nls.h`, and `linux/errno.h` are declared at lines 10-14.
- No callable functions, exported symbols, module init/exit code, or `struct nls_table` definitions are present within lines 1-3984.
- The visible public-facing behavior is data-only: static `const wchar_t` translation arrays used later by `char2uni()` through `page_charset2uni[]`.

## Data Tables

- `c2u_81` starts at line 16 and establishes the recurring table shape: 256 `wchar_t` entries indexed by CP936 trail byte. Invalid/unassigned entries are `0x0000`.
- The chunk defines complete lead-byte tables from `c2u_81` through `c2u_F0`, plus the first visible rows of `c2u_F1`.
- Symbol/compatibility zones appear in `A1-A9`: punctuation/math, Roman numerals, fullwidth ASCII, Hiragana/Katakana, Greek, Cyrillic, box drawing, phonetic/diacritic, Bopomofo-like symbols, and CJK units.
- `AA-AF` include shorter valid ranges with trailing zero fill; later tables return to full GBK/CP936 character ranges.
- Lines 3938-3972 define complete `c2u_F0`.
- Lines 3974-3984 start `c2u_F1` and cover only offsets `0x00-0x4F`; the table continues in the next chunk.

## Control Flow

There is no executable control flow in this chunk. The implied later lookup is:

- First CP936 byte selects a table pointer such as `c2u_81`.
- Second byte indexes that table.
- `0x0000` means unmapped/invalid.

Adjacent context confirms `char2uni()` later selects `page_charset2uni[ch]`, indexes by `cl`, rejects `0x0000`, and returns two consumed bytes for double-byte mappings.

## State And Dependencies

- All tables here are `static const`, immutable, and file-local.
- No runtime state, allocation, locks, reference counts, or mutable globals are introduced.
- Depends on later `page_charset2uni[]` to make these arrays reachable.
- Depends on later NLS registration to expose charset `"cp936"` and alias `"gb2312"`.

## Risks And Cross-Chunk References

- `0x0000` is both invalid sentinel and Unicode NUL, so double-byte table lookups cannot represent Unicode NUL.
- `0x7F` is consistently zeroed and should be rejected as an invalid trail byte.
- Malformed low trail bytes rely on zero entries plus later rejection.
- The chunk boundary is inside the `c2u_F1` initializer; this chunk is not syntactically complete by itself.
- Next chunk must continue and close `c2u_F1`, then define later decode tables and the reverse/registration logic.

### Chunk 2: lines 3985-8212

# Chunk Research: sources/os/linux/linux/fs/nls/nls_cp936.c lines 3985-8212

## Scope

This chunk is static lookup data for the Linux NLS CP936/GB2312 charset module. It contains no executable functions or exported symbols. The visible content is split between:

- The tail of charset-to-Unicode `c2u_*` tables, including the end of `c2u_F1` and full/partial pages `c2u_F2` through `c2u_FE`.
- The dispatch table `page_charset2uni[256]`.
- The beginning and large middle of Unicode-to-charset `u2c_*` tables, from `u2c_00` through a partial `u2c_7A`.

## APIs And Data Structures

The chunk defines internal `static const` data only:

- `static const wchar_t c2u_F2[256]` through `c2u_FE[256]`, plus the tail of `c2u_F1`, map CP936 lead-byte pages to Unicode code points. Each table is indexed by the second byte of a two-byte CP936 sequence.
- `static const wchar_t *page_charset2uni[256]` maps a CP936 first byte to the corresponding `c2u_*` table. Entries for unmapped lead bytes are `NULL`; entries `0x81` through `0xFE` point to the corresponding page tables.
- `static const unsigned char u2c_00[512]` through `u2c_7A[512]` begin the reverse mapping. Each Unicode high-byte page table stores 256 pairs of bytes, so index `low_byte * 2` gives the first CP936 byte and `low_byte * 2 + 1` gives the second. `0x00, 0x00` means no reverse mapping for that Unicode scalar in that page.

Adjacent code outside this chunk shows how these data structures are consumed:

- `char2uni()` uses `page_charset2uni[ch]` and then indexes `[cl]`.
- `uni2char()` uses `u2c_00` specially for Unicode page `0x00`, otherwise uses the later `page_uni2charset[ch]` dispatcher.
- The Euro sign is a special case outside this chunk: CP936 byte `0x80` maps to Unicode `0x20ac`.

## Control Flow

There is no runtime control flow in this chunk. The only control relationship is table-driven:

- For CP936-to-Unicode conversion, the first input byte selects a `c2u_*` page through `page_charset2uni`; the second input byte indexes the selected page.
- For Unicode-to-CP936 conversion, later code selects a `u2c_*` page by the high byte of the Unicode value and indexes a two-byte pair by the low byte.
- `NULL` dispatch entries and `0x0000`/`0x00,0x00` cells are sentinel states interpreted by later conversion routines as unmappable or invalid.

## State And Dependencies

All state here is immutable module-local lookup state:

- The `c2u_*` tables depend on definitions from earlier chunks: `page_charset2uni` references `c2u_81` through `c2u_F0` that are defined before this line range.
- This chunk also begins the `u2c_*` table family but does not complete it. Later chunks define `u2c_7B` and beyond, the `page_uni2charset[256]` dispatcher, case-fold tables, NLS callbacks, and module registration.
- The file depends on Linux kernel NLS infrastructure outside this chunk through later `struct nls_table` registration, but this chunk itself has no direct include or function dependency.

## Notable Table Coverage

Visible `c2u_*` coverage:

- `c2u_F1` tail at the beginning of the chunk.
- Full `c2u_F2` to `c2u_F7`.
- Shorter terminal pages `c2u_F8` to `c2u_FE`, where many high second-byte positions are `0x0000`.

Visible `u2c_*` coverage:

- Low Unicode pages: `u2c_00`, `u2c_01`, `u2c_02`, `u2c_03`, `u2c_04`.
- Symbol/punctuation pages: `u2c_20` through `u2c_26`.
- CJK compatibility and kana-like ranges: `u2c_30` through `u2c_33`.
- Main CJK Unified Ideographs pages: `u2c_4E` through the partial `u2c_7A`.

## Risks And Edge Cases

- Table integrity is the primary risk. A single misplaced byte pair or `wchar_t` value silently changes filename transcoding behavior.
- Sentinel ambiguity is intentional but fragile: `0x0000` and `0x00,0x00` mean unmapped in table cells, while adjacent code treats Unicode `U+0000` specially through `u2c_00`.
- The chunk boundary splits both logical table families: it starts mid-`c2u_F1` and ends mid-`u2c_7A`. Review or regeneration must include adjacent chunks to validate initializer completeness.
- Reverse mappings are not guaranteed to be visually obvious inverses of the forward mappings; correctness depends on generated table consistency across the whole file.
- `page_charset2uni` depends on all `c2u_*` page symbols being present and ordered correctly. A wrong pointer affects an entire lead-byte page.

## Cross-Chunk References

- Previous chunk: defines earlier `c2u_81` through `c2u_F1` content used by `page_charset2uni`.
- Next chunk: continues `u2c_7A`, defines later `u2c_*` pages, then defines `page_uni2charset`, `charset2lower`, `charset2upper`, `uni2char()`, `char2uni()`, and module registration.
- Final merge should describe this file as a generated/static NLS mapping module whose behavior is almost entirely determined by these table families plus the small conversion callbacks later in the file.

### Chunk 3: lines 8213-11112

# Chunk Research: sources/os/linux/linux/fs/nls/nls_cp936.c lines 8213-11112

## Scope

- Repository subset: `Docs/research_subset_a.md`; `sources/os/linux/linux` is explicitly in scope.
- Source span read: lines 8213-11112 of `fs/nls/nls_cp936.c`.
- This is chunk 3 of the oversized CP936/GB2312 Linux NLS module. It starts at the tail of `u2c_7A[512]`, then completes the Unicode-to-CP936 mapping tables, defines the Unicode-page dispatch table, byte-wise case tables, conversion callbacks, NLS table registration, and module metadata.
- This report is chunk-only and does not create or replace the final per-file report.

## APIs And Entry Points

- `uni2char(const wchar_t uni, unsigned char *out, int boundlen)` encodes a Unicode `wchar_t` to CP936 bytes. It returns bytes written, `-ENAMETOOLONG` for too-small output buffers, or `-EINVAL` for unmapped Unicode.
- `char2uni(const unsigned char *rawstring, int boundlen, wchar_t *uni)` decodes CP936 input to Unicode. It returns bytes consumed, `-ENAMETOOLONG` for empty input, or `-EINVAL` for invalid double-byte table entries.
- `table` is the `struct nls_table` exposed to the Linux NLS core with `.charset = "cp936"`, `.alias = "gb2312"`, the two conversion callbacks, and the byte case tables.
- `init_nls_cp936()` calls `register_nls(&table)`.
- `exit_nls_cp936()` calls `unregister_nls(&table)`.
- `module_init`, `module_exit`, `MODULE_DESCRIPTION`, `MODULE_LICENSE`, and `MODULE_ALIAS_NLS(gb2312)` provide module lifecycle and metadata.

## Data Structures

- The chunk finishes `u2c_7A[512]` from the previous chunk, then defines `u2c_7B` through `u2c_9F`, plus sparse/special pages `u2c_DC`, `u2c_F9`, `u2c_FA`, `u2c_FE`, and `u2c_FF`.
- Each `u2c_*[512]` table is indexed by `Unicode_low_byte * 2`; the two bytes at that offset are the CP936 encoded form. `{0x00, 0x00}` is the unmapped sentinel.
- Several terminal pages are intentionally sparse or partially initialized. Because the arrays have fixed size 512, omitted initializer cells are zero-filled by C and therefore behave as unmapped entries.
- `page_uni2charset[256]` maps a Unicode high byte to the corresponding `u2c_*` page. Unsupported high-byte pages are `NULL`.
- `charset2lower[256]` and `charset2upper[256]` are ASCII-only byte case maps: `A-Z` and `a-z` fold normally, while bytes `0x80..0xff` are identity.

## Control Flow

`uni2char()`:

- Rejects `boundlen <= 0` before writing.
- Special-cases Unicode `U+20AC` to single byte `0x80`.
- For Unicode page `0x00`, reads `u2c_00[cl * 2]` and `u2c_00[cl * 2 + 1]`. If the pair is zero and `cl < 0x80`, it emits the ASCII byte directly, including `U+0000`; if `cl >= 0x80`, it returns `-EINVAL`.
- For nonzero Unicode high bytes, selects `page_uni2charset[ch]`. A `NULL` page returns `-EINVAL`.
- Requires `boundlen > 1` before writing any two-byte mapping.
- Writes the two-byte table result, then rejects `{0x00, 0x00}` with `-EINVAL`.

`char2uni()`:

- Rejects `boundlen <= 0`.
- For `boundlen == 1`, decodes byte `0x80` as `U+20AC`; all other single bytes map directly to the same Unicode value, including high bytes that might otherwise be double-byte leads if more input were available.
- For longer input, reads `ch = rawstring[0]` and `cl = rawstring[1]`.
- Selects `page_charset2uni[ch]` from earlier chunks. If the page exists and `cl` is nonzero, it indexes `charset2uni[cl]`; `0x0000` is invalid, otherwise two bytes are consumed.
- If no page exists or `cl == 0`, it falls back to a one-byte mapping, again special-casing `0x80` to `U+20AC`.

## State And Dependencies

- All lookup tables and the `nls_table` are file-local static objects; there is no dynamic allocation, locking, reference counting, or mutable conversion state.
- The executable code depends on `page_charset2uni` and `c2u_*` tables from chunks 1 and 2 for CP936-to-Unicode decoding.
- `uni2char()` depends on `u2c_00` through `u2c_7A` from chunk 2 and the remaining `u2c_*` pages in this chunk.
- Registration depends on Linux NLS infrastructure from `linux/nls.h`; errors are Linux errno values from earlier includes.
- The case maps are handed to the NLS core and operate on encoded bytes, not Unicode scalars.

## Risks And Edge Cases

- Table integrity is the dominant risk. A wrong byte pair, wrong dispatcher pointer, or misplaced zero sentinel silently changes filename transcoding for filesystems using `cp936`/`gb2312`.
- `uni2char()` writes table-derived two-byte output before checking for `{0x00, 0x00}`, so a caller can observe modified output bytes even when `-EINVAL` is returned.
- `char2uni()` treats a lone high byte as a valid one-byte Unicode value when `boundlen == 1`; incomplete double-byte input is not reported as `-EINVAL` or `-ENAMETOOLONG`.
- `char2uni()` rejects double-byte mappings with trail byte `0x00` by falling back to a one-byte decode of the lead byte.
- Unicode values are effectively limited to the low 16 bits of `wchar_t` by `ch = (uni >> 8) & 0xff` and `cl = uni & 0xff`.
- `U+0000` is explicitly allowed in the `uni2char()` ASCII fallback, while `0x0000` in double-byte decode tables and `{0x00, 0x00}` in reverse tables are invalid sentinels.
- There is no Unicode normalization, width folding, or Chinese character case folding; case conversion is ASCII byte-only.

## Cross-Chunk References

- Chunk 1 defines the early `c2u_81` onward byte-to-Unicode tables used indirectly by this chunk's `char2uni()`.
- Chunk 2 completes the later `c2u_*` tables, defines `page_charset2uni`, defines `u2c_00` through the partial `u2c_7A`, and is required for both callbacks in this chunk to compile and behave correctly.
- This chunk completes the reverse mapping set and owns the actual NLS callbacks and module lifecycle. Any final per-file analysis must merge all three chunks because decoding and encoding use independent table families connected only by the callbacks and dispatch tables.
