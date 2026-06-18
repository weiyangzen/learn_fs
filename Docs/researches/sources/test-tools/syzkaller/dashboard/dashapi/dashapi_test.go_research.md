# sources/test-tools/syzkaller/dashboard/dashapi/dashapi_test.go Research

## Purpose
This Go test verifies option handling in `dashapi.New`, specifically whether a custom `UserAgent` option alters the request constructor embedded in `Dashboard`.

## Important APIs
- `TestNewOpts` defines table cases for no options and a custom user agent.
- It constructs `Dashboard` with optional `UserAgent`, invokes `dash.ctor`, and checks the `User-Agent` header.

## Control flow
For each subtest, the code builds an option slice, calls `New`, fails on unexpected constructor error, creates a sample GET request, and compares the header against the expected string.

## State and persistence
No persistent state. It uses in-memory request construction with `bytes.NewBuffer`.

## Dependencies and integration points
Depends on `testing`, `bytes`, and the client constructor in `dashapi.go`. It provides direct regression coverage for the option path that wraps `http.NewRequest`.

## Risks
Coverage is narrow: it does not verify `NewCustom`, bearer auth, transport encoding, retry behavior, or default HTTP behavior. The error message's wanted value is hardcoded to the custom-agent text even in the no-option case, though the comparison remains correct.

## Test signals
Running `go test ./dashboard/dashapi` would execute this table test and compile the dashboard API structs. This research pass did not run tests.
