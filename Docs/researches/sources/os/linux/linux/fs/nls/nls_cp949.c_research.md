# File Research: sources/os/linux/linux/fs/nls/nls_cp949.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-3981, source bytes 262119, report `Docs/researches/chunks/chunk_sources_os_linux_linux_fs_nls_nls_cp949_c_1_1_3981_0dac1408871b_research.md`
- chunk 2: lines 3982-8200, source bytes 262112, report `Docs/researches/chunks/chunk_sources_os_linux_linux_fs_nls_nls_cp949_c_2_3982_8200_94a3971fa371_research.md`
- chunk 3: lines 8201-12440, source bytes 262096, report `Docs/researches/chunks/chunk_sources_os_linux_linux_fs_nls_nls_cp949_c_3_8201_12440_f5b501257056_research.md`
- chunk 4: lines 12441-13947, source bytes 88972, report `Docs/researches/chunks/chunk_sources_os_linux_linux_fs_nls_nls_cp949_c_4_12441_13947_41931786529c_research.md`

## Chunk Research

### Chunk 1: lines 1-3981

# Chunk Research: sources/os/linux/linux/fs/nls/nls_cp949.c lines 1-3981

## Scope

This chunk is the opening data segment of the Linux NLS CP949/EUC-KR charset module. It contains the file banner, kernel includes, and the first byte-to-Unicode translation pages. It does not contain the executable conversion functions or module registration code; those appear later in the file.

## APIs and Public Surface

- Includes kernel module/NLS dependencies: `<linux/module.h>`, `<linux/kernel.h>`, `<linux/string.h>`, `<linux/nls.h>`, and `<linux/errno.h>` at lines 10-14.
- Defines only `static const` data, so nothing in this chunk is exported directly.
- The arrays in this chunk are private implementation data for later NLS callbacks, especially the later `char2uni()` path that indexes `page_charset2uni[first_byte][second_byte]`.

## Data Defined

- Lines 16-3966 define complete `static const wchar_t c2u_*[256]` pages for CP949 lead bytes: `c2u_81` through `c2u_C8`, then `c2u_CA` through `c2u_F0`.
- `c2u_C9` is deliberately absent in this range. Later `page_charset2uni` context maps the C9 lead-byte slot to `NULL`, so C9 is treated as an unmapped lead page rather than a missing symbol.
- Lines 3968-3981 begin `c2u_F1[256]` but stop mid-initializer at the `0x60-0x67` row. The table continues in the next chunk.
- Most early pages use 256 explicit entries, where `0x0000` marks unmapped byte positions. Several compatibility/symbol pages have shorter initializers; C zero-initialization fills the trailing entries.
- The chunk contains 112 table declarations total: 111 complete tables plus the partial `c2u_F1`.

## Table Semantics

- Each `c2u_XX` table maps a CP949 two-byte sequence whose first byte is `0xXX`; the second byte is used as the direct 0-255 array index.
- `0x0000` is the invalid/unmapped sentinel, not a valid translation result for multibyte CP949 entries.
- The first groups (`0x81` onward) map mostly Hangul syllables in the Unicode `0xAC00` range and beyond.
- The `0xA1`-`0xAC` region includes symbols, punctuation, compatibility jamo, Greek/Cyrillic, kana, and enclosed/alphanumeric symbols alongside Hangul-extension entries.
- The `0xCA`-`0xF0` pages contain mostly Hanja/CJK compatibility mappings, including private/compatibility-style Unicode values such as `0xF9xx`.

## Control Flow

There is no executable control flow in this chunk. Runtime behavior is data-driven: later `char2uni()` reads a first byte, fetches the matching page pointer from `page_charset2uni`, indexes by the second byte, and rejects `0x0000`. Later ASCII/single-byte fallback behavior is outside this chunk.

## State and Dependencies

All tables are `static const`, file-local, immutable module-lifetime data. There is no locking, allocation, reference counting, or mutable global state in this chunk.

The data depends on Linux NLS conventions from `<linux/nls.h>`, C static array zero-fill semantics, and later file-local pointer tables that make these pages reachable from conversion callbacks.

## Risks and Cross-Chunk References

The main correctness risk is table integrity: a shifted, missing, or mistyped value changes filename transcoding behavior for that CP949 byte pair. Since `0x0000` drives invalid-character handling, accidental zeros can reject valid names, while accidental nonzero values can admit invalid byte sequences.

`c2u_F1` begins here and continues after line 3981. Later chunks define `c2u_F2` through `c2u_FD`, `page_charset2uni`, Unicode-to-charset tables, case-conversion tables, `uni2char()`, `char2uni()`, `struct nls_table`, and module init/exit.

### Chunk 2: lines 3982-8200

# Chunk Research: sources/os/linux/linux/fs/nls/nls_cp949.c lines 3982-8200

## Scope

- Repository subset: `Docs/research_subset_a.md`; `sources/os/linux/linux` is explicitly in scope.
- Source span read: lines 3982-8200 of `fs/nls/nls_cp949.c`.
- This is chunk 2 of a chunked Linux NLS CP949/UHC module. It begins inside the byte-to-Unicode table for lead byte `0xF1`, completes byte-to-Unicode pages through `0xFD`, defines the byte-to-Unicode lead-byte index, and defines the first large block of Unicode-to-CP949 reverse lookup pages.
- The chunk ends inside `u2c_7A[512]`; it does not include the rest of the reverse Unicode pages, `page_uni2charset`, case tables, conversion callbacks, `struct nls_table`, registration functions, or module metadata.

## APIs and Data Structures

- `c2u_F1[256]` tail plus complete `c2u_F2` through `c2u_FD`: `static const wchar_t` byte-to-Unicode pages for high CP949 lead bytes. Entries before the valid trail-byte area are mostly `0x0000`; populated positions map CP949 two-byte sequences to Unicode scalar values, including ordinary CJK ideographs and compatibility/private-use style values such as `U+F9FC..U+FA0B`.
- `page_charset2uni[256]`: top-level lead-byte dispatch table for the later CP949 byte decoder. It maps lead bytes `0x81..0xC8`, skips `0xC9`, then maps `0xCA..0xFD`; all other entries are `NULL`. This table references `c2u_81` through `c2u_FD`, many of which are defined in earlier chunks.
- `u2c_01`, `u2c_02`, `u2c_03`, `u2c_04`, `u2c_11`, `u2c_20` through `u2c_26`, `u2c_30` through `u2c_33`, and `u2c_4E` through the first part of `u2c_7A`: `static const unsigned char [512]` reverse lookup pages. Each Unicode low byte consumes two array bytes at offsets `low * 2` and `low * 2 + 1`; `{0x00, 0x00}` means unmapped.
- The reverse pages cover Latin Extended and spacing marks (`U+0100..U+02FF`), Greek (`U+03xx`), Cyrillic (`U+04xx`), Hangul Jamo (`U+11xx`), punctuation/currency/symbol/box-drawing blocks (`U+20xx..U+26xx`), CJK symbols and Hangul compatibility jamo (`U+30xx..U+33xx`), and a dense run of CJK ideograph pages from `U+4E00` through `U+7Axx`.

## Control Flow

There are no functions, loops, or conditional branches in this chunk. Runtime behavior is implicit in how later callbacks consume these tables:

- CP949-to-Unicode conversion will use the first byte as an index into `page_charset2uni`. If the selected page pointer is `NULL`, or the selected trail-byte slot contains `0x0000`, the later decoder rejects the sequence.
- Unicode-to-CP949 conversion will use the Unicode high byte to select one of the `u2c_*` pages through `page_uni2charset` in a later chunk. Once a page is selected, the Unicode low byte indexes a two-byte output pair.
- Sparse reverse pages rely on zero pairs as the invalid sentinel. Single-byte ASCII and any special non-table paths are necessarily handled outside this chunk by the later conversion functions.

## State and Dependencies

- All visible state is immutable `static const` lookup data. There is no allocation, locking, reference counting, I/O, or module lifecycle code in this span.
- The arrays depend on kernel types and NLS contracts introduced earlier in the file, especially `wchar_t` and the later `struct nls_table` callback signatures from Linux NLS headers.
- `page_charset2uni` depends on byte-to-Unicode page arrays defined outside this chunk (`c2u_81` through `c2u_F0`) as well as the pages completed here.
- The reverse `u2c_*` pages depend on a later `page_uni2charset` index table to be reachable. Pages defined here but omitted from that later index would be dead data.

## Risks and Edge Cases

- Data integrity is the primary risk. These generated constants are the conversion behavior; an incorrect literal silently corrupts filename encoding/decoding for filesystems using NLS `cp949`.
- Chunk boundaries split logical declarations. The chunk starts after `c2u_F1` has already been declared and ends before `u2c_7A` closes, so merge validation must combine adjacent chunks before checking table completeness.
- `0x0000` in `c2u_*` and `{0x00, 0x00}` in `u2c_*` are sentinels, not mappings.
- The lead-byte index deliberately leaves `0xC9`, `0xFE`, and `0xFF` unmapped while allowing broad `0x81..0xFD` coverage.
- CP949/UHC contains compatibility and vendor-extension mappings. Values in the `U+F9xx` and `U+FAxx` areas and extended byte pairs in `0xCA..0xFD` are intentional compatibility behavior.

## Cross-Chunk References

- Earlier chunk(s) define the file prologue, kernel includes, generated-table comment, `c2u_81` through most of `c2u_F1`, and any special high-ASCII reverse table used by `uni2char`.
- This chunk's `page_charset2uni` references `c2u_81..c2u_F0` from earlier chunk(s) and `c2u_F1..c2u_FD` from the boundary/current span.
- Later chunk(s) continue and close `u2c_7A[512]`, define additional reverse pages beyond `U+7Axx`, build `page_uni2charset[256]`, and define case tables plus `uni2char`, `char2uni`, the `nls_table`, init/exit registration, and module metadata.
- The final per-file report must be produced only after all chunks for `sources/os/linux/linux/fs/nls/nls_cp949.c` are available; this chunk report intentionally does not create that merged artifact.

### Chunk 3: lines 8201-12440

# Chunk Research: sources/os/linux/linux/fs/nls/nls_cp949.c lines 8201-12440

## Scope

This report covers only `sources/os/linux/linux/fs/nls/nls_cp949.c` lines 8201-12440 in learn_fs subset A (`Docs/research_subset_a.md`). I read the requested range completely and used adjacent context to identify the enclosing conversion-table declarations and their consumers. The chunk is immutable CP949 Unicode-to-charset lookup data, not executable control code.

## APIs And Data Surface

This chunk contributes `static const unsigned char u2c_*[512]` tables used by the file-local `uni2char()` callback registered with the Linux NLS core. Each table is keyed by the high byte of a Unicode code point; the low byte indexes a pair of bytes at `cl * 2` and `cl * 2 + 1`. A `{0x00, 0x00}` pair means there is no CP949 mapping for that Unicode code point.

The chunk begins inside `u2c_7A` (declared at line 8195 in the previous chunk) and includes its tail through line 8261. It then contains complete tables `u2c_7B` through `u2c_C5`, and starts `u2c_C6` at line 12405. The requested range ends inside `u2c_C6` after entries for low-byte range `0x84-0x87` at line 12440; the remainder of `u2c_C6` is in the next chunk.

Complete table declarations visible in this range are:

- `u2c_7B` at lines 8263-8324.
- `u2c_7C` at lines 8326-8392.
- `u2c_7D` at lines 8394-8459.
- `u2c_7E` at lines 8461-8503.
- `u2c_7F` at lines 8505-8571.
- `u2c_80` through `u2c_89` at lines 8573-9250.
- `u2c_8A` through `u2c_8F` at lines 9252-9630.
- `u2c_90` through `u2c_9F` at lines 9632-10635.
- `u2c_AC` through `u2c_AF` at lines 10637-10907.
- `u2c_B0` through `u2c_BF` at lines 10909-11995.
- `u2c_C0` through `u2c_C5` at lines 11997-12403.

## Control Flow

There are no functions, branches, loops, allocations, locking operations, I/O calls, or module side effects in this chunk. Runtime control flow is indirect through adjacent code:

1. `uni2char()` splits `wchar_t uni` into `ch = (uni >> 8) & 0xff` and `cl = uni & 0xff`.
2. It selects `page_uni2charset[ch]`.
3. If a page table exists, it requires at least two output bytes, copies `table[cl * 2]` and `table[cl * 2 + 1]`, and rejects the mapping with `-EINVAL` when both bytes are zero.
4. If no page table exists but `ch == 0 && cl != 0`, it emits a one-byte ASCII character.
5. Otherwise, it reports `-EINVAL`.

The tables in this chunk are therefore passive data for Unicode-to-CP949 conversion only. CP949-to-Unicode conversion uses the separate `c2u_*` tables and `page_charset2uni[]` from earlier chunks.

## State And Dependencies

All state in this range is file-local, read-only, and initialized at compile time. There is no mutable state and no synchronization requirement.

The chunk depends on the later `page_uni2charset[256]` dispatcher, which references every complete page here: `u2c_7B` through `u2c_9F`, `u2c_AC` through `u2c_AF`, and `u2c_B0` through `u2c_C6`. It also depends on the later `uni2char()` bounds and zero-pair checks for safety. Kernel-facing integration comes from the adjacent `struct nls_table table`, which exposes the file-local conversion callbacks as charset `cp949` with alias `euc-kr` via `register_nls()`.

## Risks And Invariants

The critical invariant is the fixed 512-byte shape: each table must contain 256 two-byte mappings, and `uni2char()` assumes `cl * 2 + 1` is valid for any low byte. Sparse ranges must use explicit `0x00, 0x00` pairs, not omitted entries, because table offsets are positional.

A single incorrect byte changes filename/text transcoding semantics and can create non-round-tripping behavior against the earlier `c2u_*` tables. The risk is highest at chunk boundaries: this range begins in the middle of `u2c_7A` and ends in the middle of `u2c_C6`, so validation of those two tables must include adjacent chunks. The densely populated Hangul syllable tables from `u2c_AC` onward show sequential CP949 byte-pair progressions; accidental insertion or deletion would shift every subsequent mapping.

The data is not self-validating. Safer checks are generated-table comparison against the authoritative CP949 mapping source, compile-time size checks if the file is ever refactored, and round-trip tests covering mapped values, unmapped zero pairs, ASCII fallback, and multibyte output buffer limits.

## Cross-Chunk References

Previous chunk: defines the start of `u2c_7A` at line 8195 and the earlier Unicode page tables and `page_charset2uni[]` used for reverse conversion. This chunk only contains the tail of `u2c_7A`, so its integrity cannot be evaluated from this range alone.

Next chunk: continues `u2c_C6` from line 12441, then defines `u2c_C7` and later Unicode-to-charset tables, the `page_uni2charset[]` dispatcher at line 13755, case-conversion tables, `uni2char()`, `char2uni()`, `struct nls_table`, and module init/exit registration.

### Chunk 4: lines 12441-13947

# Chunk Research: sources/os/linux/linux/fs/nls/nls_cp949.c lines 12441-13947

## Scope

This chunk is the tail of the Linux kernel CP949/EUC-KR NLS module. It covers the end of the generated Unicode-to-charset lookup data, the page index used by Unicode encoding, ASCII-only case tables, the two conversion callbacks exported through `struct nls_table`, and module registration metadata.

## APIs and Entry Points

- `uni2char(const wchar_t uni, unsigned char *out, int boundlen)` at lines 13861-13890 is the Unicode-to-CP949 encoder callback assigned to `table.uni2char`.
- `char2uni(const unsigned char *rawstring, int boundlen, wchar_t *uni)` at lines 13892-13921 is the CP949-to-Unicode decoder callback assigned to `table.char2uni`.
- `static struct nls_table table` at lines 13923-13930 publishes charset name `"cp949"`, alias `"euc-kr"`, conversion callbacks, and case tables to the kernel NLS core.
- `init_nls_cp949()` and `exit_nls_cp949()` at lines 13932-13940 register/unregister the table via `register_nls(&table)` and `unregister_nls(&table)`.
- `module_init`, `module_exit`, `MODULE_DESCRIPTION`, `MODULE_LICENSE`, and `MODULE_ALIAS_NLS(euc-kr)` at lines 13942-13947 expose this as a loadable NLS module.

## Data and State

- Lines 12441-12471 finish `u2c_C6`, whose declaration begins before this chunk. This is a cross-chunk continuation and should be merged with chunk 3 data context.
- Lines 12473-13604 define `u2c_C7` through `u2c_D7`, each as `static const unsigned char [512]`. Each table maps a Unicode low byte to two CP949 bytes for one Unicode high-byte page. Indexing is `cl * 2` and `cl * 2 + 1`.
- Lines 13606-13608 define sparse `u2c_DC` data containing only zero entries for this generated page. It is still referenced from `page_uni2charset`, so zeros are meaningful invalid-entry sentinels rather than unused memory.
- Lines 13610-13691 define sparse compatibility/private mapping pages `u2c_F9` and `u2c_FA`, with many zero pairs marking unmapped Unicode codepoints.
- Lines 13693-13753 define `u2c_FF`, including fullwidth ASCII/punctuation and Hangul compatibility mappings, again using `0x00, 0x00` for invalid slots.
- Lines 13755-13787 define `page_uni2charset[256]`, the top-level Unicode high-byte dispatch table for `uni2char`. Non-null entries point to `u2c_*` tables defined across this file; many referenced tables are outside this chunk.
- Lines 13789-13823 and 13825-13859 define `charset2lower` and `charset2upper`. Only ASCII A-Z/a-z fold; bytes `0x80-0xff` are identity-preserving, so CP949 multibyte bytes are not case-normalized.
- The chunk has no runtime-owned mutable state except the static `table` registration with the NLS subsystem. Conversion state is entirely table-driven and stack-local.

## Control Flow

- `uni2char` first rejects `boundlen <= 0` with `-ENAMETOOLONG`.
- It splits `wchar_t uni` into `ch = high byte` and `cl = low byte`, then looks up `page_uni2charset[ch]`.
- If a page table exists, it requires room for two bytes (`boundlen > 1`), emits the two-byte table entry, rejects `0x00,0x00` as `-EINVAL`, and returns `2`.
- If no page table exists and the Unicode value is non-NUL ASCII (`ch == 0 && cl`), it emits one byte and returns `1`.
- Otherwise `uni2char` returns `-EINVAL`. Notably, U+0000 is not encoded by the ASCII fallback because `cl` must be nonzero.
- `char2uni` rejects `boundlen <= 0` with `-ENAMETOOLONG`.
- If only one input byte is available, it maps that byte directly to Unicode and returns `1`.
- With at least two bytes, it uses `rawstring[0]` as a charset page selector into `page_charset2uni` and `rawstring[1]` as the low-byte index. `page_charset2uni` is defined earlier in the file, outside this chunk.
- If a decode page exists and the second byte is nonzero, it loads `charset2uni[cl]`, rejects Unicode `0x0000` as `-EINVAL`, and returns `2`.
- Otherwise it falls back to single-byte identity decoding of the first byte and returns `1`.

## Dependencies

- Kernel headers used by this chunk are declared at file top outside the line range: `<linux/module.h>`, `<linux/kernel.h>`, `<linux/string.h>`, `<linux/nls.h>`, and `<linux/errno.h>`.
- `register_nls`, `unregister_nls`, `struct nls_table`, module macros, and `MODULE_ALIAS_NLS` come from the Linux NLS/module infrastructure.
- Error returns use `-ENAMETOOLONG` and `-EINVAL`.
- `char2uni` depends on `page_charset2uni` and `c2u_*` tables defined in earlier chunks.
- `page_uni2charset` depends on many `u2c_*` tables defined in earlier chunks plus the `u2c_C7`-`u2c_D7`, `u2c_DC`, `u2c_F9`, `u2c_FA`, and `u2c_FF` tables defined here.

## Risks and Edge Cases

- The generated mapping tables are correctness-critical; a single byte-pair error silently corrupts filename/string conversion for the affected codepoint.
- `0x00,0x00` is the invalid-entry sentinel for `uni2char`, while Unicode `0x0000` is the invalid-entry sentinel for `char2uni`. Any legitimate mapping to NUL would be impossible through these paths.
- `char2uni` treats `boundlen == 1` as a valid one-byte identity mapping. If a buffer ends after the first byte of an intended CP949 two-byte sequence, this callback does not report truncation; callers must supply correct bounds and interpret returned byte counts.
- The decoder requires `cl != 0` before using a two-byte page. A zero second byte forces single-byte fallback for `ch`.
- ASCII case folding is byte-oriented only. This is appropriate for NLS table callbacks, but callers should not expect Korean or fullwidth case transformations.
- The `page_uni2charset` table references sparse pages (`u2c_DC`, `u2c_FA`, `u2c_FF`) where most entries are invalid; conversion behavior depends on the zero-pair sentinel check staying intact.

## Cross-Chunk References

- The chunk starts inside `u2c_C6`; its declaration and earlier entries are in the previous chunk.
- Earlier chunks define all `c2u_*` tables and `page_charset2uni`, which are required by `char2uni`.
- Earlier chunks also define `u2c_01` through `u2c_C6`; this chunk completes the Unicode-to-charset table set and builds `page_uni2charset` over both earlier and local `u2c_*` arrays.
- This chunk contains the final module registration, so merge output should connect earlier generated tables to the `struct nls_table` callbacks and kernel NLS registration here.
