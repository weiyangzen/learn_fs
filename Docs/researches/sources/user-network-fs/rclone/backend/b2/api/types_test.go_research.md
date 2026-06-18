# Research: sources/user-network-fs/rclone/backend/b2/api/types_test.go

## Purpose
This file tests the B2 API `Timestamp` helper semantics: millisecond JSON encoding/decoding, zero detection, and equality behavior.

## Important APIs, Types, and Functions
- Package-level fixtures define `emptyT`, `t0` at `1970-01-01T01:01:01.123456789Z`, and `t1` at `2001-02-03T04:05:06.123000000Z`.
- `TestTimestampMarshalJSON` calls `MarshalJSON` directly and compares decimal millisecond strings.
- `TestTimestampUnmarshalJSON` parses a millisecond number and compares the resulting `time.Time`.
- `TestTimestampIsZero` checks zero and nonzero values.
- `TestTimestampEqual` asserts that zero timestamps are never equal and nonzero timestamps compare as expected.

## Control Flow
The tests directly invoke methods rather than going through `encoding/json`. They use `require.NoError` before assertions where parsing/marshaling can fail. Equality tests include same-value comparisons with gocritic suppressions because identical receiver/argument calls are intentional.

## State and Persistence Behavior
No persistent state is touched. Fixtures are immutable package variables for test use.

## Dependencies and Integration Points
The test imports the `api` package externally as `api_test`, which validates exported behavior only. It uses rclone `fstest.Time` to create fixed UTC times and `testify` for assertions.

## Risks and Edge Cases
- Direct `MarshalJSON` calls do not test standard `encoding/json` interaction with pointer receiver methods.
- Tests do not cover invalid unmarshal input, negative or zero epoch values, sub-millisecond truncation beyond the selected fixture, filename version helpers, or `Error.Fatal`.
- The marshal expectation for `t0` confirms truncation from `.123456789` to `.123`, but this is implicit rather than named in the test.

## Test Signals
The tests pin the B2 timestamp contract and the deliberately nonstandard zero equality behavior, providing regression coverage for API time conversion.
