# sources/user-network-fs/samba/source4/dsdb/tests/python/sort.py

## Purpose

`sort.py` validates Samba LDAP server-side sort behavior for AD user attributes. It creates a configurable number of test users with deliberately varied values, requests results through the `server_sort` control, and compares returned order against expected files generated from known behavior. It covers simple ASCII-ish data and a Unicode-heavy set intended to match Windows Server 2012 R2 ordering for difficult strings.

## Important APIs, Types, and Functions

The module uses `SamDB.search()` with controls like `server_sort:1:<reverse>:<attr>` and `server_sort:1:<reverse>:<attr>:<matching-rule-oid>`. `norm()` decodes bytes as UTF-8 when needed, normalizes with Unicode NFKC, and uppercases before comparison. `FIENDISH_TESTS` is a curated list of strings containing whitespace, fractions, combining-looking characters, embedded NULs, fullwidth text, case variants, diacritics, punctuation, and CJK text.

`BaseSortTests` owns test data creation, expected-result loading, cleanup, and shared assertions. `create_user()` constructs user attributes that exercise binary, numeric, timestamp, and locale-like sort behavior. `SimpleSortTests` sets `avoid_tricky_sort = True` and uses `simplesort.expected`; `UnicodeSortTests` uses full Unicode data and `unicodesort.expected`.

## Control Flow

At startup the script requires `DATA_DIR` for expected result files and `SERVER` for the host. Test setup opens `SamDB`, creates `ou=sort,<base_dn>`, creates `opts.elements` users, partitions attributes into binary-sorted, numeric-sorted, timestamp, int64, and locale-sorted sets, computes expected binary order directly in Python, and loads locale expected order from the results file.

`_test_server_sort_default()` loops over locale-sorted attributes and forward/reverse directions, requesting only the sorted attribute and comparing normalized returned values to expected order. `_test_server_sort_binary()` compares binary-like attributes with Python string order. `_test_server_sort_us_english()` repeats locale sorting with the AD matching rule OID `1.2.840.113556.1.4.1499`. `_test_server_sort_different_attr()` sorts by one attribute while returning a different attribute, computes expected pairs locally with binary, locale, or numeric comparators, and asserts the sort attribute is not returned unless requested.

## State and Persistence Behavior

Every test setup creates an OU and `opts.elements` users in the target directory. Teardown deletes the OU with `tree_delete:1`. The suite persists no files, but it reads expected files from `DATA_DIR`. The test data includes embedded NULs and non-ASCII values in AD attributes, so storage and retrieval paths must preserve those values enough for sort comparison.

## Dependencies and Integration Points

This file integrates with the LDAP server-side sort control implementation, schema syntax handling for binary/numeric/time attributes, matching-rule OID handling, LDB controls, Samba's `cmp` compatibility helper, Python locale collation, and external expected-result fixtures. It also uses `system_session(lp)` for privileged setup and cleanup.

## Risks and Edge Cases

The explicit `locale.setlocale(locale.LC_ALL, ('en_US', 'UTF-8'))` can fail on systems without that locale. The script requires environment variables rather than using the positional host argument for the final host value; missing `DATA_DIR` or `SERVER` exits before tests. Expected ordering is intentionally Windows-specific and can diverge from Python or Samba's local collation. Timestamp sorting has a documented Windows failure note in the diagnostic path. Embedded NUL values and Unicode normalization make this a sensitive regression test for string handling.

## Test Signals

Passing tests show that Samba's server-side sort returns the same ordered values as the expected fixtures for default and US English matching-rule sorts, handles binary-like and numeric attributes separately, honors reverse sorting, supports sorting by an attribute not returned in the result set, and keeps the unrequested sort attribute out of returned entries.
