# sources/user-network-fs/rclone/backend/swift/swift_internal_test.go

## Purpose

This file unit-tests Swift backend helpers for URL encoding and `Retry-After` handling.

## Important APIs, Types, and Functions

`TestInternalUrlEncode` checks `urlEncode` preserves alphanumerics, `/`, `.`, `_`, and `-`, while percent-encoding spaces, `&`, punctuation, and UTF-8 bytes. `TestInternalShouldRetryHeaders` checks `shouldRetryHeaders` for Swift 429 errors with short and long `Retry-After` values.

## Control Flow

The URL test iterates known input/output pairs. The retry test constructs Swift headers and a `swift.Error{StatusCode: 429}`, verifies a one-second retry-after sleeps and returns `retry=true`, then changes the header to `3600` and verifies it returns a `fserrors.RetryAfter` without sleeping.

## State and Persistence Behavior

No persistent state is used. The short retry test intentionally waits for roughly one second.

## Dependencies and Integration Points

It depends on `github.com/ncw/swift/v2`, rclone `fserrors`, `testify/assert`, and the unexported helpers in `swift.go`.

## Risks and Edge Cases

The URL test logs mismatches but does not call `t.Errorf` or assert, so a mismatch may not fail the test. The sleep-based retry test adds wall-clock cost and may be timing-sensitive.

## Test Signals

Passing retry assertions confirm short retry-after delays are obeyed inline and long delays become scheduler-visible retry-after errors. URL encoding should be strengthened with assertions to protect DLO manifest paths.
