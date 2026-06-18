# sources/test-tools/syzkaller/pkg/html/urlutil/urls_test.go

## Purpose
`urls_test.go` verifies query-parameter removal behavior for URL helper functions.

## Important APIs, Types, And Functions
`TestDropParam` defines table-driven cases for `DropParam` and uses testify `assert.Equal` for comparisons.

## Control Flow
The test iterates four cases: removing a key entirely, removing a second key while preserving duplicate first keys, removing all duplicates for a key, and removing only a specific duplicate value. Each case calls `DropParam` and compares to the expected URL string.

## State And Persistence Behavior
The test is pure and in-memory. It relies on deterministic `net/url` query encoding order for the provided keys.

## Dependencies And Integration Points
It imports `testing` and `github.com/stretchr/testify/assert`. It exercises only `DropParam`, indirectly covering `TransformParam`.

## Risks And Edge Cases
There are no cases for `SetParam`, invalid URLs, encoded characters, fragments, absolute URLs, or retaining a key with an empty value. Because `assert` continues after failures, multiple mismatches can be reported in one run.

## Test Signals
A failure indicates a regression in duplicate-value filtering or query deletion. Passing gives confidence for common dashboard filter-removal links.
