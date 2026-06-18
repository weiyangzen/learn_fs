# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/gbk.c

## Purpose

`gbk.c` is a generated/static mapping asset for the Plan 9/9front `tcs` character set converter. It exports `tabgbk[]`, a GBK-code-indexed table whose values are Unicode `Rune` code points or `-1` for unmapped/invalid GBK byte pairs.

## Structure

- Includes only `gbk.h`.
- Defines one global symbol: `long tabgbk[]`.
- Contains no functions, conditionals, macros, or executable logic.
- Full-file validation:
  - Lines: 4006
  - Bytes: 223095
  - SHA-256: `b2ac4e3446d8dbfdb344f9ba3c9d4822762ead7ca484b73b511279c7cca2eec5`
  - Table tokens: 32016
  - Mapped entries: 21791
  - `-1` holes: 10225
  - Lowest mapped value: `0x00a4`
  - Highest mapped value: `0xffe5`
  - CJK Unified Ideograph entries in `0x4e00..0x9fa5`: 20902
  - CJK Compatibility Ideograph entries in `0xf900..0xfaff`: 21
  - Values above BMP: 0
  - Duplicate mapped Unicode values: 0

## Indexing Contract

The table is intended to be addressed as:

`tabgbk[gbk_code - GBKMIN]`

where `GBKMIN` is `0x8140` and consumer code treats `GBKMAX` as an exclusive upper bound. The populated token count, 32016, matches the exclusive range `0x8140..0xfe4f`.

## Integration Points

- Declared by `gbk.h` as `extern long tabgbk[]`.
- Consumed by `conv_gbk.c`:
  - GBK input conversion looks up `tabgbk[c - GBKMIN]`.
  - GBK output conversion builds a reverse `Rune -> GBK code` table from `tabgbk`.
- Registered in `tcs.c` through the `"gbk"` converter entries that point to `gbk_in` and `gbk_out`.

## Important Notes

The table deliberately contains many `-1` sentinels for holes in the GBK byte-pair space. Any reverse-map builder must skip negative entries before indexing by the mapped Unicode value. The neighboring `conv_gbk.c` reverse-map loop should be reviewed with this in mind, because this table itself does not protect consumers from using `-1` as an array index.
