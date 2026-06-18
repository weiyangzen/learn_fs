# File Research: sources/os/linux/linux-stable/fs/unicode/Makefile

## Summary
Builds the Unicode normalization implementation, generated data table, KUnit tests, and optional host-side data generator.

## Main Contents
- Builds `unicode.o` from `utf8-norm.o` and `utf8-core.o`.
- Builds `utf8data.o` when `CONFIG_UNICODE` is enabled.
- Builds `tests/utf8_kunit.o` for normalization tests.
- Defines generation of `utf8data.c` either by copying `utf8data.c_shipped` or regenerating from Unicode Character Database text files.
- Registers host program `mkutf8data`.

## Important Behavior
Normal builds copy the checked-in generated data file. Passing `REGENERATE_UTF8DATA=1` invokes `mkutf8data` with DerivedAge, DerivedCombiningClass, DerivedCoreProperties, UnicodeData, CaseFolding, NormalizationCorrections, and NormalizationTest inputs.

## Dependencies
Uses Linux kbuild object, host program, target, and `if_changed` rules.

## Risks
Regeneration depends on all expected UCD files being present in the directory and matching the parser assumptions in `mkutf8data.c`.
