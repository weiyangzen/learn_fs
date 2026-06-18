# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_ja_jis_to_unicode.h

## Role

Kernel-only Japanese JIS-family to Unicode mapping header for illumos `kiconv_ja` conversions. It is almost entirely static lookup data plus two small compatibility macros for Microsoft-flavored mappings.

## Structure

- Lines 1-66: CDDL header, Sun copyright, Unicode data permission notice, and note that Sun modified the Unicode data.
- Lines 68-78: include guard, C++ linkage wrapper, includes of `<sys/kiconv.h>` and `<sys/kiconv_ja.h>`, then `_KERNEL` gating.
- Line 80: defines local `NODEST` as `KICONV_JA_REPLACE`; unmapped table cells therefore yield U+FFFD replacement, not `KICONV_JA_NODEST`.
- Lines 85-118: `kiconv_ja_jisx0201roman_to_ucs2[]`, a 128-entry direct table for JIS X 0201 Roman/control bytes 0x00-0x7f. It mostly maps byte values to the same UCS-2 code point.
- Lines 120-136: `kiconv_ja_jisx0201kana_to_ucs2[]`, a 63-entry table for JIS X 0201 half-width kana 0xa1-0xdf to Unicode U+FF61-U+FF9F.
- Lines 138-2394: `kiconv_ja_jisx0208_to_ucs2[]`, a dense 94x94-style JIS X 0208 mapping table. It starts with punctuation, symbols, Greek/Cyrillic, kana, box drawing, vendor rows, then kanji. Undefined positions use `NODEST`. Later rows include private-use sequential mappings such as U+E000 and above for vendor/private areas.
- Lines 2396-4653: `kiconv_ja_jisx0212_to_ucs2[]`, a second 94x94-style table for JIS X 0212 supplemental mappings. Early rows are sparse with many `NODEST` entries, then extended Latin/Greek/Cyrillic and large CJK ranges, ending with compatibility/private-use rows.
- Lines 4655-4674: `KICONV_JA_CNV_JISMS_TO_U2(id, u, c1, c2)` macro. It initializes `u` to `KICONV_JA_NODEST` and applies a small set of EUCJP-MS/CP932 overrides for JIS X 0208 coordinates: `(0x21,0x41)->0xff5e`, `(0x21,0x42)->0x2225`, `(0x21,0x5d)->0xff0d`, `(0x21,0x71)->0xffe0`, `(0x21,0x72)->0xffe1`, and `(0x22,0x4c)->0xffe2`.
- Lines 4676-4685: `KICONV_JA_CNV_JIS0212MS_TO_U2(id, u, c1, c2)` macro. It initializes `u` to `KICONV_JA_NODEST` and maps EUCJP-MS/CP932 JIS X 0212 coordinate `(0x22,0x43)` to `0xffe4`.
- Lines 4687-4695: undefines `NODEST`, closes `_KERNEL`, C++ wrapper, and guard.

## Dependencies And Consumers

- Depends on `kiconv_ja_ucs2_t`, `KICONV_JA_REPLACE`, `KICONV_JA_NODEST`, `KICONV_JA_TBLID_EUCJP_MS`, and `KICONV_JA_TBLID_CP932` from `kiconv_ja.h`.
- `kiconv_ja_ucs2_t` is `ushort_t`, so all lookup results are 16-bit. This fits the UCS-2-oriented Japanese conversion path in this header.
- The arrays are declared `static const` in a header, so every translation unit including it gets private read-only copies. This is consistent with generated kiconv mapping headers but increases object size.
- The data is consumed by Japanese kernel conversion code that indexes by normalized JIS row/cell or byte offsets. Bounds checks must live in callers; the tables themselves do not validate indices.

## Important Behaviors

- Regular table misses use U+FFFD replacement via `NODEST`, whereas the Microsoft override macros use `KICONV_JA_NODEST` (0xffff) to signal "no override." Callers must distinguish these meanings.
- The X 0201 Roman table maps byte 0x5c to U+005C rather than a yen sign. Any yen/backslash policy is handled elsewhere or through other mapping tables.
- The X 0201 kana table is offset-based; callers must subtract the start byte 0xa1 before indexing.
- The X 0208 and X 0212 tables are arranged in 94-cell rows using comments like `/* 16 01 */`; callers normally subtract 0x21 from each JIS byte and compute `row * 94 + cell`.
- CP932/EUCJP-MS compatibility mappings are not embedded by rewriting the main tables. They are exposed as explicit coordinate overrides, making standard and Microsoft behavior share the same base data.

## Risks And Gotchas

- The file is data-heavy and generated-data-like. Manual edits are risky because one shifted entry corrupts all later row/cell mappings.
- `NODEST` is a temporary macro with a generic name, but the file undefines it before exit. Include-order issues are low as long as no code relies on `NODEST` after including this header.
- The `KICONV_JA_CNV_*` macros are multi-statement macros without `do { } while (0)`. They should be used only in statement contexts where the expanded `if` chain cannot break surrounding `else` binding.
- Because the static arrays are header-local, duplicate inclusion in multiple C files can duplicate large constants. This is a size tradeoff, not a runtime mutability issue.

## Research Notes

Read completely: 4695 lines, 179489 bytes.
