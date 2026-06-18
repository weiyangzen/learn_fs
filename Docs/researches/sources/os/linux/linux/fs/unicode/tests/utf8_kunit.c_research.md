# File Research: sources/os/linux/linux/fs/unicode/tests/utf8_kunit.c

## Purpose
KUnit tests for Linux filesystem UTF-8 normalization, casefolding, comparisons, and supported Unicode versions.

## Main Contents
- Test vectors:
  - `nfdi_test_data[]` covers identity normalization, canonical decomposition, non-canonical compatibility exclusions, Greek mapping, and canonical combining class ordering.
  - `nfdicf_test_data[]` covers ASCII folding, sharp-s expansion, decomposed casefolding, Cherokee, Old Hungarian, Osage, Latin small-capital, and Georgian cases.
- Local wrappers:
  - `utf8len()` calls `utf8nlen()` with NUL-terminated length.
  - `utf8cursor()` calls `utf8ncursor()` with NUL-terminated length.
- Test cases:
  - `check_utf8_nfdi()`: verifies normalized length and byte stream for NFDI.
  - `check_utf8_nfdicf()`: verifies normalized length and byte stream for NFDICF.
  - `check_utf8_comparisons()`: verifies `utf8_strncmp()` and `utf8_strncasecmp()` equivalence behavior.
  - `check_supported_versions()`: verifies expected supported and unsupported Unicode versions.
- KUnit suite setup:
  - `init_test_ucd()` loads `UTF8_LATEST`.
  - `exit_test_ucd()` unloads it.
  - `unicode_normalization_test_suite` registers four tests.

## Important Design Points
- Tests exercise both length calculation and cursor byte emission.
- Comparison tests validate higher-level exported API behavior, not only internal normalization.
- Tests require the generated table to be loadable via `utf8_load()`.

## Cross-File Relationships
- Includes `../utf8n.h` for internal cursor APIs.
- Calls exported APIs from `utf8-core.c` and internal/test-exported APIs from `utf8-norm.c`.
- Built only when `CONFIG_UNICODE_NORMALIZATION_KUNIT_TEST` is enabled.

## Risks / Review Notes
- Some `qstr.len` values use `sizeof()` on fixed-size arrays, so they include trailing zero padding; this intentionally exercises length-bounded handling but differs from ordinary filename lengths.
- `init_test_ucd()` records an expectation if `utf8_load()` fails but still returns 0; subsequent tests depend on `test->priv` being valid.
