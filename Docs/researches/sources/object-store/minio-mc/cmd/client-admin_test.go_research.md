# sources/object-store/minio-mc/cmd/client-admin_test.go

## Purpose

`client-admin_test.go` provides an HTTP handler helper for admin policy request tests.

## Important APIs, Types, and Functions

`adminPolicyHandler` stores endpoint, policy name, and expected policy bytes. Its `ServeHTTP` handles authenticated PUT requests and validates content length and body length.

## Control Flow

The handler rejects missing `Authorization` with 403. On PUT, it parses `Content-Length`, copies exactly that many bytes from the body, checks that received length matches expected policy length, and returns 200 with zero content length. Other methods return 403.

## State and Persistence Behavior

There is no persistence. The handler stores expected test state in memory.

## Dependencies and Integration Points

It integrates with tests that exercise admin policy upload behavior through HTTP.

## Risks and Edge Cases

The handler checks body length but not byte equality. Unused fields such as endpoint/name may be for compatibility with broader tests.

## Test Signals

Useful signals are status codes for missing auth, bad length, short body, correct PUT, and unsupported methods.
