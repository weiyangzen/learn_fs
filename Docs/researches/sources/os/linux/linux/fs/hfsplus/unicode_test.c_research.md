# File Research: sources/os/linux/linux/fs/hfsplus/unicode_test.c

## Role

KUnit test suite for HFS+ Unicode string operations. It tests string comparison, Unicode-to-Linux conversion, Linux-to-Unicode conversion, dentry hashing, dentry comparison, special character mapping, buffer limits, corrupted lengths, and casefold/decomposition flag behavior.

## Test Fixtures and Helpers

- `struct test_mock_string_env` bundles two `hfsplus_unistr` values, a scratch buffer, and buffer size.
- `setup_mock_str_env()` and `free_mock_str_env()` allocate/free string test state.
- `create_unistr()` builds a simple big-endian HFS+ Unicode string from ASCII bytes.
- `corrupt_unistr()` sets length to `U16_MAX` to exercise defensive clamping.
- `struct test_mock_sb` embeds a mock `nls_table`, `hfsplus_sb_info`, and `super_block`.
- `setup_mock_sb()` initializes mock UTF-8 NLS state, attaches `sb.s_fs_info`, and clears `HFSPLUS_SB_NODECOMPOSE` and `HFSPLUS_SB_CASEFOLD`.
- `test_uni2char()` emits ASCII characters directly and `?` for non-ASCII.
- `test_char2uni()` converts one input byte to a Unicode code point.
- `setup_mock_dentry()` assigns the mock superblock to a static dentry.
- `create_qstr()` builds qstrs for hash/compare tests.

## Covered Behavior

- `hfsplus_strcasecmp_test()`
  - Identical strings, case-insensitive equality, ordering, prefix/length ordering, empty strings, single characters, maximum-length strings, mid-string differences, and corrupted overlong lengths.
- `hfsplus_strcmp_test()`
  - Case-sensitive equality/ordering, prefix/length ordering, empty strings, maximum-length strings, mid-string differences, and corrupted overlong lengths.
- `hfsplus_unicode_edge_cases_test()` and `hfsplus_unicode_boundary_test()`
  - Non-ASCII code units, embedded NUL code units, maximum length, last-character differences, zero-length strings, and single-character-vs-empty comparisons.
- `hfsplus_uni2asc_*` tests
  - Basic ASCII conversion, empty/single-character conversion, HFS+ NUL and slash mapping, mixed special characters, buffer-too-small handling, exact-size buffers, zero-length buffers, corrupted HFS+ lengths, maximum-length strings, and non-ASCII fallback behavior in the mock NLS table.
- `hfsplus_asc2uni_*` tests
  - Basic ASCII conversion, explicit lengths with embedded NULs, colon-to-slash mapping, multiple special characters, exact/excess/zero output limits, partial input lengths, printable ASCII, and decomposition flag behavior for simple ASCII.
- `hfsplus_hash_dentry_*` tests
  - Basic hashing, identical-string stability, empty/single-character hashing, casefold disabled/enabled behavior, colon/slash equivalence, decomposition flag behavior, consistency across repeated hashes, different-string hash differences, long names, printable punctuation, and embedded NULs.
- `hfsplus_compare_dentry_*` tests
  - Identical/different strings, empty-string ordering, casefold disabled/enabled behavior, colon/slash equivalence, length differences, decomposition flag behavior, long names, single-character differences, embedded NULs, printable punctuation, and combined casefold/decomposition flag behavior.

## Suite Registration

- `hfsplus_unicode_test_cases[]` registers 27 KUnit cases.
- `hfsplus_unicode_test_suite` names the suite `hfsplus_unicode`.
- `kunit_test_suite()` registers the suite.
- Module metadata describes the suite, uses GPL licensing, and imports the `EXPORTED_FOR_KUNIT_TESTING` namespace.

## Dependencies

Includes KUnit, NLS, dcache, stringhash, and `hfsplus_fs.h`. It depends on KUnit-visible exports from `unicode.c`.

## Research Notes

The tests are focused on algorithmic Unicode behavior with mock NLS callbacks rather than mounting real HFS+ media. They provide regression coverage for edge cases that can affect catalog lookup and dcache consistency: overlong HFS+ string lengths, casefold-dependent equality, colon/slash compatibility mapping, embedded NUL handling, and output length failures.
