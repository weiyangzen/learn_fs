# File Research: sources/os/linux/linux-stable/fs/hfsplus/unicode_test.c

## Role

KUnit test suite for HFS+ Unicode string operations in `unicode.c`.

## Test Harness

- `struct test_mock_string_env`
  - Holds two `hfsplus_unistr` values plus an output/input buffer.
- `setup_mock_str_env()` / `free_mock_str_env()`
  - Allocate/free string test environment and buffer.
- `create_unistr()`
  - Builds a simple HFS+ Unicode string from ASCII bytes.
- `corrupt_unistr()`
  - Sets length to `U16_MAX` to exercise length-clamping behavior.
- `struct test_mock_sb`
  - Minimal mocked superblock, HFS+ superblock info, and NLS table.
- `setup_mock_sb()` / `free_mock_sb()`
  - Initializes mocked NLS and HFS+ flags.
- `test_uni2char()`
  - ASCII-only `uni2char` mock; non-ASCII becomes `?`, no space returns `-ENAMETOOLONG`.
- `test_char2uni()`
  - Single-byte `char2uni` mock.
- `setup_mock_dentry()` and `create_qstr()` support hash/compare tests.

## Covered Functions

The suite covers:

- `hfsplus_strcasecmp()`
- `hfsplus_strcmp()`
- `hfsplus_uni2asc_str()`
- `hfsplus_asc2uni()`
- `hfsplus_hash_dentry()`
- `hfsplus_compare_dentry()`

## Test Categories

- String comparison:
  - identical strings
  - case-insensitive equality
  - case-sensitive inequality
  - lexicographic ordering
  - different lengths
  - empty strings
  - single characters
  - maximum HFS+ length
  - corrupted overlarge lengths
  - special Unicode codepoints
  - embedded NUL code units
- Unicode-to-ASCII/NLS conversion:
  - basic ASCII conversion
  - empty and single-character strings
  - NUL and slash compatibility mapping
  - mixed special characters
  - insufficient/exact/zero output buffers
  - corrupted length correction
  - maximum length strings
  - non-ASCII fallback behavior through mocked NLS
- ASCII/NLS-to-Unicode conversion:
  - basic ASCII
  - explicit source length with embedded NUL tail ignored
  - colon-to-slash mapping
  - repeated special characters
  - max-length and over-length behavior
  - zero max length
  - printable ASCII and embedded NUL
  - nodecompose flag behavior for simple ASCII
- Dentry hashing:
  - nonzero hashes
  - identical strings produce identical hashes
  - casefold disabled/enabled behavior
  - colon/slash normalization
  - consistency and simple distribution checks
  - long names, printable ASCII, embedded NUL
- Dentry comparison:
  - identical strings
  - lexicographic ordering
  - empty/non-empty ordering
  - casefold disabled/enabled behavior
  - colon/slash normalization
  - length parameter behavior
  - nodecompose flag behavior for simple ASCII
  - long strings and end differences
  - embedded NUL
  - combined casefold/nodecompose flag states

## Suite Registration

- `hfsplus_unicode_test_cases[]` registers 27 KUnit cases.
- `hfsplus_unicode_test_suite` is named `"hfsplus_unicode"`.
- Uses `kunit_test_suite()`.
- Module metadata declares GPL license and imports `EXPORTED_FOR_KUNIT_TESTING`.

## Research Notes

The tests use simplified mock NLS behavior, so they validate control flow, flag behavior, buffer handling, and HFS+/Linux special-character mapping more than full real-world UTF-8 conversion. Several tests exercise corrupted length handling introduced in `unicode.c` by expecting clamping rather than crashes or out-of-bounds traversal.
