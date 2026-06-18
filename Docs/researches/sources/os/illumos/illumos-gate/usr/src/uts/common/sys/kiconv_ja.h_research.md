# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_ja.h

## Purpose

`kiconv_ja.h` is the shared Japanese kernel iconv support header. It defines encoding table IDs, conversion helper macros, byte-classification predicates, NEC/IBM remapping logic, Japanese mapping typedefs, and compact static lookup vectors for JIS/SJIS transformations.

The file is guarded by `_SYS_KICONV_JA_H`, includes `<sys/kiconv.h>`, and uses C++ `extern "C"` wrapping.

## Public Surface

Encoding/table IDs:

- `KICONV_JA_TBLID_EUCJP`
- `KICONV_JA_TBLID_EUCJP_MS`
- `KICONV_JA_TBLID_SJIS`
- `KICONV_JA_TBLID_CP932`
- `KICONV_JA_MAX_MAPPING_TBLID`

Replacement/sentinel values:

- `KICONV_JA_DEF_SINGLE`
- `KICONV_JA_REPLACE (0xfffd)`
- `KICONV_JA_NODEST (0xffff)`
- surrogate range predicates `KICONV_JA_IFHISUR()` and `KICONV_JA_IFLOSUR()`

Conversion helper macros include:

- `KICONV_JA_RETERROR`
- `KICONV_JA_NGET`
- `KICONV_JA_NGET_REP_FR_MB`
- `KICONV_JA_NGET_REP_TO_MB`
- `KICONV_JA_NPUT`
- `KICONV_JA_GETU`
- `KICONV_JA_PUTU`
- UTF-8 BOM skip macros with and without conversion state

The macro layer assumes caller-local variables and labels such as `errno`, `rv`, `ret`, `next`, `ip`, `op`, `ileft`, `oleft`, `read_len`, `l`, `repnum`, and `kcd`.

## Byte Classification

The header defines predicates for:

- ASCII and C1 controls.
- EUC-JP codeset 1, codeset 2, codeset 3, UDC ranges, and JIS X 0208 row coverage.
- SJIS hankaku katakana, multibyte lead bytes, kanji lead bytes, supplemental kanji, UDC, IBM, NEC/IBM, and trail bytes.
- UTF-8 private-use/UDC range `0xe000` through `0xf8ff`.

These macros centralize byte-range policy for EUC-JP, EUC-JP-MS, SJIS, and CP932 conversion paths.

## Mapping Data

The file defines:

- `typedef ushort_t kiconv_ja_euc16_t`
- `typedef ushort_t kiconv_ja_ucs2_t`

It then provides six static mapping vectors:

- `kiconv_ja_sjtojis1`
- `kiconv_ja_sjtojis2`
- `kiconv_ja_jis208tosj1`
- `kiconv_ja_jis212tosj1`
- `kiconv_ja_jistosj2`
- `kiconv_ja_sjtoibmext`

These support direct conversion between SJIS byte positions and JIS row/cell values, plus IBM extension remapping. Invalid or unmappable vector entries use `0xff` or `0xffff` sentinels.

## NEC/IBM Remapping

`KICONV_JA_REMAP_NEC(dest)` translates selected NEC/IBM SJIS extension ranges into IBM code ranges. If the input is outside the accepted ranges, it sets `dest` to `0xffff`.

This macro mutates its argument repeatedly, so it must be called with a simple lvalue, not an expression with side effects.

## Dependencies And Integration

Direct dependency:

- `<sys/kiconv.h>` for common kiconv state/types and replacement definitions.

Observed related headers:

- `kiconv_ja_unicode_to_jis.h` includes this file and uses `KICONV_JA_NODEST`, table IDs, and `kiconv_ja_euc16_t`.
- `kiconv_ja_jis_to_unicode.h` includes this file and uses `KICONV_JA_REPLACE`, table IDs, and `kiconv_ja_ucs2_t`.
- `uts/common/sys/Makefile` exports `kiconv_ja.h`.

The helper macros call external conversion helpers such as `read_unicode()` and `write_unicode()` and depend on `kiconv_state_t` state for BOM processing.

## Control Flow

Unlike pure data-table headers, this file embeds control flow in macros. The macros decrement input/output counters, advance pointers, set `errno`, set `rv`, increment replacement counts, and jump to caller labels.

This makes the header tightly coupled to expected conversion-function structure. It reduces repeated boilerplate in the Japanese converters but makes misuse easy outside that context.

## Risks And Invariants

Important invariants:

- Table IDs must remain synchronized with companion Japanese mapping headers.
- Sentinel values `0xff`, `0xffff`, and `0xfffd` have distinct meanings and should not be collapsed.
- Byte-classification macros assume unsigned/`ushort_t`-style values; signed `char` inputs must be promoted safely before use.
- BOM macros mutate `inbuf` and `inleft`; callers must pass lvalue pointer/count variables.

Risks:

- Macro control flow depends on caller variables and labels, so refactoring callers can silently break these macros.
- `KICONV_JA_REMAP_NEC` mutates its argument and evaluates it many times.
- Static arrays in a header can duplicate storage in each including translation unit.
- The conversion tables are compact but opaque; changes should be validated with known EUC-JP, SJIS, CP932, surrogate, UDC, and BOM test vectors.
