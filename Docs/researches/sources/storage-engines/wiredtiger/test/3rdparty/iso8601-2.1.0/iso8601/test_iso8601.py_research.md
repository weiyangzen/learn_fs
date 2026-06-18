<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/iso8601-2.1.0/iso8601/test_iso8601.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/iso8601-2.1.0/iso8601/test_iso8601.py

Purpose: Pytest/Hypothesis test suite for the vendored `iso8601` parser.

Important APIs/functions: `test_iso8601_regex`, `test_fixedoffset_eq`, default-timezone tests, parameterized `test_parse_invalid_date`, parameterized `test_parse_valid_date`, and two Hypothesis property tests for naive and timezone-aware datetimes.

Control flow: Invalid cases assert `is_iso8601` is false and `parse_date` raises `ParseError` with expected message prefix. Valid cases assert regex acceptance, field-by-field equality, complete datetime equality, isoformat expectations, deepcopy, pickle, and parse round-trip. Hypothesis tests serialize generated datetimes with `isoformat` and require exact parse equality.

State and persistence behavior: No durable state. Property tests may generate many cases and print debug representations during runs.

Dependencies and integration points: Depends on pytest, hypothesis, hypothesis.extra.pytz, pickle/copy, datetime, and local `.iso8601`. It is the primary quality gate for the parser.

Risks: Hypothesis timezone-aware equality can expose edge cases around pytz timezone offsets and fold/ambiguous times. Tests assume generated `datetime.isoformat()` strings are within parser support. The debug `print` calls can produce noisy logs. Some expected invalid cases only assert message prefix, not exact details.

Test signals: Passing this suite gives strong confidence for accepted date formats, regression issues, timezone offsets, fractions, and round-trip behavior. It also signals packaging dev dependencies from `pyproject.toml` are available.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/iso8601-2.1.0/iso8601/test_iso8601.py -->
