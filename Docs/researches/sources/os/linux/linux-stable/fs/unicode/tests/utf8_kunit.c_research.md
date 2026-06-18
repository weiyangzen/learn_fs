# File Research: sources/os/linux/linux-stable/fs/unicode/tests/utf8_kunit.c

## Summary
KUnit test suite for Linux UTF-8 normalization and casefolding support.

## Key Tests
- `check_supported_versions()`
- `check_utf8_comparisons()`
- `check_utf8_nfdicf()`
- `check_utf8_nfdi()`
- Suite setup/teardown: `init_test_ucd()`, `exit_test_ucd()`

## Important Behavior
The test data covers direct ASCII, canonical decomposition, canonical ordering, non-canonical compatibility cases that must not decompose under NFD, Greek normalization correction behavior, full casefolding, multi-character folds such as sharp-s, and codepoints introduced in newer Unicode versions.

Tests compare `utf8nlen()` lengths against expected normalized byte lengths, then iterate normalized bytes with `utf8byte()` and compare every output byte. Comparison tests ensure `utf8_strncmp()` and `utf8_strncasecmp()` report equality between original and expected normalized/casefolded forms.

Version tests assert support for Unicode 7.0.0, 9.0.0, and `UTF8_LATEST`, and reject unsupported future/zero/invalid ages.

## Dependencies
Uses KUnit, `linux/unicode.h`, internal `utf8n.h`, and `utf8_load()`/`utf8_unload()` to access generated Unicode tables.

## Risks
The test suite is focused on representative normalization/casefold examples, not exhaustive UCD coverage. Exhaustive validation is handled by `mkutf8data.c` during data generation.
