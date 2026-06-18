<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/generic-handlers_contrib.go -->
# sources/object-store/minio/cmd/generic-handlers_contrib.go

## Purpose
Adds a request classifier for login and STS requests that should bypass bucket federation and upload forwarding middleware.

## Important APIs, types, and functions
- `guessIsLoginSTSReq` returns true for `/login...` paths or POST `/` requests authenticated as STS.

## Control flow
The function rejects nil requests, checks path prefix against `loginPathPrefix`, then checks for root-path POST with `authTypeSTS`.

## State and persistence behavior
No state is mutated or persisted. It reads request method/path and computed auth type.

## Dependencies and integration points
Used by generic forwarding middleware to avoid proxying login/STS calls as bucket traffic. Depends on `loginPathPrefix`, `SlashSeparator`, and `getRequestAuthType`.

## Risks and edge cases
The classifier is intentionally broad for `/login` prefixes. Incorrect classification can route authentication requests through bucket federation or skip forwarding for legitimate object paths that match the login prefix.

## Test signals
No direct tests in this group. Behavior is indirectly covered by auth, browser login, STS, and federation middleware tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/generic-handlers_contrib.go -->
