# File Research: sources/virtualization/nvme-cli/util/suffix.c

## Role

`suffix.c` implements formatting and parsing helpers for SI decimal suffixes and binary suffixes. These utilities are used to present or accept human-readable NVMe sizes and counts.

## SI Suffix Formatting

`si_suffixes` is ordered from largest to smallest:

- Q 1e30
- R 1e27
- Y 1e24
- Z 1e21
- E 1e18
- P 1e15
- T 1e12
- G 1e9
- M 1e6
- k 1e3

`suffix_si_get_ld()` scans this table and, for the first magnitude less than or equal to the input, divides the input `long double` in place and returns the suffix. Values below 1000 return an empty suffix. `suffix_si_get()` is the `double` wrapper that converts through `long double`.

## SI Suffix Parsing

`suffix_si_parse()` parses strings of the form integer, integer plus suffix, or integer plus locale decimal fraction plus optional single-character SI suffix.

Flow:

- parse the integer part with `strtoull(str, endptr, 0)`;
- accept a plain number when the end pointer reaches NUL;
- use `localeconv()->decimal_point` to recognize the decimal separator;
- allow a suffix immediately after the integer part;
- otherwise parse fractional digits after the decimal point;
- reject more than one suffix character;
- find the suffix in `si_suffixes`;
- scale the integer part by repeated multiply-by-10 and align the fractional part to the suffix exponent;
- return the sum in `*val`.

If no suffix remains and no invalid trailing text exists, it returns the integer part.

## Binary Suffix Formatting

`binary_suffixes` contains:

- Pi, shift 50
- Ti, shift 40
- Gi, shift 30
- Mi, shift 20
- Ki, shift 10

`suffix_binary_get()` accepts a signed `long long *`, checks absolute value, rounds by adding half the unit before shifting, updates the value in place, and returns a suffix.

`suffix_dbinary_get()` accepts a `double *`, divides by the matching power-of-two unit without integer rounding, updates the value in place, and returns a suffix.

## Binary Suffix Parsing

`suffix_binary_parse()` parses an unsigned integer with `strtoull()`, accepts plain numbers, then recognizes two-character suffixes case-insensitively against the table. On match it left-shifts by the suffix amount and returns the scaled value.

## Dependencies

Uses C library parsing/formatting and math headers, locale support, and `common.h` for `ARRAY_SIZE`.

## Notable Edge Cases

- SI parsing has a comment noting overflow should be checked, but repeated multiplication of `num` and `frac` currently has no overflow guard.
- Binary parsing left-shifts without overflow checking.
- SI parsing is locale-sensitive for decimal separators.
- Binary parsing requires two suffix characters such as `Ki`; a single `K` is not accepted.

## Research Notes

This file treats SI and binary suffixes as separate grammars. SI supports fractional values such as decimal input with `k/M/G/...`, while binary parsing is integer-only.
