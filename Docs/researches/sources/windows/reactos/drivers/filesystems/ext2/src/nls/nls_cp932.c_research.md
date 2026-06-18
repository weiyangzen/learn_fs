# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp932.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-3983, source bytes 262092, report `Docs/researches/chunks/chunk_sources_windows_reactos_drivers_filesystems_ext2_src_nls_nls_cp932_c_1_1_f426f8f9e1c8_research.md`
- chunk 2: lines 3984-7946, source bytes 250878, report `Docs/researches/chunks/chunk_sources_windows_reactos_drivers_filesystems_ext2_src_nls_nls_cp932_c_2_3_a63cc8c72ab7_research.md`

## Chunk Research

### Chunk 1: lines 1-3983

# Chunk Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp932.c lines 1-3983

## Scope

- Repository subset: `Docs/research_subset_a.md`; `sources/windows/reactos` is explicitly in scope.
- Source span read: lines 1-3983 of `sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp932.c`.
- This is chunk 1 of a chunked CP932/Shift-JIS NLS table source. It covers the file prologue, Linux-style NLS includes, all byte-to-Unicode page tables, the byte-to-Unicode page index, the high-ASCII reverse table, and Unicode-to-CP932 reverse pages through most of `u2c_68`.
- The chunk ends inside `u2c_68[512]`; lines 3984-3989 complete that table and line 3991 starts `u2c_69[512]`.

## APIs and Data Structures

- Header dependencies in this chunk are `<linux/module.h>`, `<linux/kernel.h>`, `<linux/string.h>`, `<linux/nls.h>`, and `<linux/errno.h>`. Although this lives under the ReactOS Ext2 source tree, this file is structurally a Linux NLS module copy/generator output.
- The generated prologue says the CP932 translation tables were generated from Microsoft Unicode code page data.
- `c2u_81` through `c2u_FC`: 45 `static wchar_t [256]` byte-to-Unicode pages for valid CP932 lead bytes:
  - `0x81..0x84`, `0x87..0x9F`
  - `0xE0..0xEA`, `0xED..0xEE`
  - `0xFA..0xFC`
- `page_charset2uni[256]` maps a lead byte to one of the `c2u_*` pages, or `NULL` when the lead byte is not a valid two-byte CP932 page.
- `u2c_00hi[256 - 0xA0][2]` maps selected Unicode `U+00A0..U+00FF` characters back to two-byte CP932 values; `{0x00, 0x00}` marks unmapped entries.
- `u2c_03`, `u2c_04`, `u2c_20` through `u2c_26`, `u2c_30`, `u2c_32`, `u2c_33`, and `u2c_4E` through the visible portion of `u2c_68` are reverse lookup pages. Each `u2c_*[512]` stores two bytes per Unicode low-byte slot.
- Visible covered character classes include Latin-1 symbols, Greek, Cyrillic, punctuation, mathematical symbols, arrows, box drawing, enclosed/compatibility forms, Hiragana, Katakana, CJK symbols, CJK ideographs from `U+4E00` through the `U+68xx` page, IBM/NEC extension ranges, and compatibility ideographs such as `U+FA0E..U+FA2D`.

## Control Flow

- There is no executable control flow in this chunk. It is table data only.
- Later conversion callbacks use these data structures:
  - CP932-to-Unicode lookup indexes `page_charset2uni[lead]`, then `c2u_*[trail]`; `NULL` pages and `0x0000` entries indicate invalid input.
  - Unicode-to-CP932 lookup chooses a reverse page from `page_uni2charset` in chunk 2, then indexes `low_byte * 2` into a `u2c_*[512]` page.
  - `u2c_00hi` is a special reverse path for `U+00A0..U+00FF`.
- ASCII and halfwidth single-byte cases are not implemented in this chunk, but the tables are arranged around those later fast paths.

## State and Dependencies

- All visible symbols have internal linkage via `static`; this chunk introduces no mutable runtime state, locks, allocation, I/O, registration, or teardown.
- The arrays are not declared `const` in this ReactOS copy, so they are writable in C type terms even though they are intended as immutable generated tables. That differs from stricter read-only table style and increases accidental-write risk.
- The tables depend on Linux NLS type/contracts (`wchar_t`, `struct nls_table`, callback signatures, `-EINVAL`) that appear later in the file. Consumers are later exposed through the module registration, not directly from this chunk.

## Risks and Edge Cases

- Any table drift or transcription error silently changes filename encoding behavior for filesystems using CP932/SJIS NLS conversion.
- `0x0000` in `c2u_*` and `{0x00, 0x00}` / byte pair `0x00,0x00` in `u2c_*` are unmapped sentinels, not valid generated double-byte mappings.
- `page_charset2uni` must stay synchronized with the available `c2u_*` arrays. A missing page makes a whole lead-byte range invalid; a wrong pointer maps an entire 256-entry plane incorrectly.
- Reverse pages depend on the exact two-byte-per-Unicode-low-byte layout. Any insertion/deletion shifts every later codepoint mapping in that page.
- CP932 intentionally includes vendor and compatibility mappings that differ from strict JIS/Shift-JIS expectations, especially NEC/IBM extension and `FAxx` compatibility ideograph ranges.
- The chunk boundary splits `u2c_68[512]`: line 3983 ends at low-byte range `0xE4-0xE7`, while lines 3984-3989 contain the remaining `0xE8-0xFF` entries and closing brace.

## Cross-Chunk References

- Chunk 2 must continue with the remainder of `u2c_68[512]`, then `u2c_69` onward through the remaining reverse tables.
- `page_uni2charset[256]`, `charset2lower[256]`, `charset2upper[256]`, `uni2char`, `char2uni`, `struct nls_table table`, init/exit registration, module metadata, and the `sjis` alias are all outside this chunk.
- Later `uni2char` should be checked against this chunk for special handling of `u2c_00hi` and reverse-page sentinel pairs.
- Later `char2uni` should be checked against this chunk for how it treats single-byte input, lead-byte bounds, `page_charset2uni`, and `0x0000` table entries.
- Linux and Linux-stable CP932 NLS files in subset A provide useful comparison points for generated-table drift and constness differences, but this report does not merge or create the final per-file report.

### Chunk 2: lines 3984-7946

# Chunk Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp932.c lines 3984-7946

## Scope

This chunk is the second ordered slice of the ReactOS ext2 CP932/SJIS NLS module. It starts in the middle of the Unicode-to-charset table section, at the tail of `u2c_68`, and runs through the end of the file. The scope is within `Docs/research_subset_a.md` because `sources/windows/reactos` is part of subset A.

The chunk contains mostly generated static data plus the executable conversion and module-registration code:

- Unicode high-byte pages `u2c_69` through `u2c_9F`, plus sparse special pages `u2c_DC`, `u2c_F9`, `u2c_FA`, and `u2c_FF`.
- The `page_uni2charset[256]` dispatch table that maps Unicode high bytes to the `u2c_*` pages.
- ASCII-oriented `charset2lower[256]` and `charset2upper[256]` casefold tables.
- `uni2char`, `char2uni`, `struct nls_table table`, `init_nls_cp932`, `exit_nls_cp932`, and module metadata.

## APIs And Data Contracts

- `uni2char(const wchar_t uni, unsigned char *out, int boundlen)` implements the NLS Unicode-to-CP932 callback. It returns a positive byte count on success and negative errno-style values on failure.
- `char2uni(const unsigned char *rawstring, int boundlen, wchar_t *uni)` implements the reverse CP932-to-Unicode callback.
- `table` exposes the charset as `"cp932"` with alias `"sjis"` through the kernel-style `struct nls_table` interface.
- `init_nls_cp932` calls `register_nls(&table)`, and `exit_nls_cp932` calls `unregister_nls(&table)`.
- `MODULE_ALIAS_NLS(sjis)` advertises the SJIS alias for module autoloading.

The data pages use a compact two-byte-per-low-byte contract. For Unicode page `0xHH`, `u2c_HH[cl * 2]` and `u2c_HH[cl * 2 + 1]` contain the CP932 byte pair for Unicode `0xHHcl`. A pair of `0x00, 0x00` means unmapped.

## Control Flow

`uni2char`:

1. Rejects `boundlen <= 0` with `-ENAMETOOLONG`.
2. Handles halfwidth katakana in Unicode page `0xFF`: for `0xFF61` through `0xFF9F`, it emits one byte `cl + 0x40`, yielding CP932 `0xA1` through `0xDF`.
3. Looks up `page_uni2charset[ch]`. If a page exists, it requires `boundlen >= 2`, reads the two-byte pair from `cl * 2`, rejects `0x0000` as `-EINVAL`, and otherwise returns `2`.
4. If `ch == 0`, it handles ASCII `0x00..0x7F` as a one-byte identity mapping. For `0x00A0..0x00FF`, it uses `u2c_00hi[cl - 0xA0]` from an earlier chunk and returns `2` only if both output bytes are nonzero.
5. All other cases return `-EINVAL`.

`char2uni`:

1. Rejects `boundlen <= 0` with `-ENAMETOOLONG`.
2. Converts ASCII `0x00..0x7F` as one-byte identity.
3. Converts CP932 halfwidth katakana `0xA1..0xDF` to Unicode `0xFF61..0xFF9F` by storing `0xFF00 | (rawstring[0] - 0x40)`.
4. Requires `boundlen >= 2` for remaining non-ASCII input.
5. Uses `page_charset2uni[ch]` from earlier chunks, indexed by second byte `cl`; if the page exists and `cl` is nonzero, it returns `2` unless the target Unicode value is `0x0000`.
6. Otherwise returns `-EINVAL`.

There is no filesystem I/O, allocation, locking, or per-mount state in this chunk. All behavior is deterministic table lookup.

## State And Dependencies

Chunk-local state:

- `u2c_69` through `u2c_9F` cover the dense CJK/Japanese Unicode page range from U+6900 through U+9FFF, with many CP932 pairs such as standard JIS bytes, IBM/NEC extension bytes, and sparse unmapped zeros.
- `u2c_DC` is a tiny sparse page with only zeros in the visible initializer.
- `u2c_F9` maps sparse compatibility/private-area entries, including one visible `0xED, 0xC4` entry and later `0xEE, 0xCD`.
- `u2c_FA` maps CJK compatibility ideographs around U+FA0C..U+FA2D to CP932 extension byte pairs.
- `u2c_FF` maps fullwidth punctuation, ASCII variants, fullwidth digits/letters, halfwidth katakana support area, and a few fullwidth symbols to CP932.
- `page_uni2charset` depends on all `u2c_*` arrays from this and earlier chunks, including pages not defined here (`u2c_03`, `u2c_04`, `u2c_20`...`u2c_68`).
- `charset2lower` and `charset2upper` perform ASCII-only case conversion. Bytes outside ASCII are identity-mapped.

Cross-chunk dependencies:

- The chunk begins after `u2c_68` has already started in chunk 1; line 3984 contains the tail of that previous page before `u2c_69` starts at line 3991.
- `uni2char` uses `u2c_00hi`, defined earlier in the file, for Unicode Latin-1 high characters.
- `char2uni` uses `page_charset2uni`, also defined earlier, for two-byte CP932-to-Unicode lookup.
- `page_uni2charset` references earlier `u2c_*` pages, so the linker/compiler needs the full translation unit, not this chunk alone.
- No later chunk exists for this file because line 7946 is the file end.

## Risks And Edge Cases

- `uni2char` checks `boundlen < 2` before looking at whether a table entry is actually unmapped. That means an unmapped non-ASCII Unicode character in a page table returns `-ENAMETOOLONG` when the caller provides only one byte of output space, rather than `-EINVAL`.
- `char2uni` treats a zero second byte as invalid even if a page exists. This is consistent with multibyte CP932 but means malformed lead-byte-plus-NUL input returns `-EINVAL`.
- The tables are declared as mutable `static unsigned char` rather than `const`, so accidental writes inside this translation unit would corrupt global conversion behavior. This chunk itself does not write to them.
- Sparse pages such as `u2c_DC`, `u2c_F9`, `u2c_FA`, and partially initialized pages rely on C zero-initialization for omitted entries. This is intentional C behavior but makes table completeness easy to misread during maintenance.
- The module advertises alias `"sjis"` while the table charset is `"cp932"`. Consumers expecting strict Shift-JIS semantics may receive Microsoft CP932 extensions, as shown by many `ED`, `EE`, `E9`, and `EA` extension mappings in this chunk.
- Case conversion is byte-oriented and only folds ASCII letters. It does not perform Unicode or Japanese-width case normalization.

## Research Notes

This chunk is primarily an NLS data-and-registration module, not ext2 filesystem logic. The executable path is limited to conversion callbacks and module init/exit. Correctness depends on table generation fidelity and consistency between the forward `u2c_*` pages here and the reverse `page_charset2uni` tables from earlier chunks.
