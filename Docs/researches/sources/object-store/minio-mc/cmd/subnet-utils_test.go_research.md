# sources/object-store/minio-mc/cmd/subnet-utils_test.go

## Purpose
Tests the basic shape of the SUBNET base URL.

## Important APIs, types, and functions
- `TestSubnetBaseURL` calls `SubnetBaseURL`, parses it as a request URI, and asserts the scheme is `https`.

## Control flow
The test obtains the base URL, parses it, fails on parse error, and checks `u.Scheme`.

## State and persistence
No state. It depends on current global dev-mode behavior only through `SubnetBaseURL`.

## Dependencies and integration points
Targets `SubnetBaseURL` from `subnet-utils.go`; uses standard `net/url` and `testing`.

## Risks and edge cases
- It does not assert host, path, dev-mode behavior, or any derived SUBNET endpoint builders.
- If `GlobalDevMode` intentionally returns non-HTTPS in some test mode, this test would fail.

## Test signals
Narrow regression guard ensuring production/default SUBNET base URL is HTTPS and syntactically valid.
