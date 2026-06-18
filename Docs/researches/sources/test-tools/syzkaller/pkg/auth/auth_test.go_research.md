# sources/test-tools/syzkaller/pkg/auth/auth_test.go

## Purpose
Unit tests for OAuth bearer subject determination.

## Important APIs, Types, and Functions
`reponseFor` creates an httptest tokeninfo server returning desired claims. Tests call `Endpoint.DetermineAuthSubj`.

## Control Flow
Cases cover valid bearer subject suffix, wrong audience, expired token, missing header, malformed/non-bearer header, and non-OK tokeninfo status.

## State and Persistence Behavior
Each test uses an in-memory HTTP server and no persistent state.

## Dependencies and Integration Points
Validates `auth.go` behavior with controlled tokeninfo responses.

## Risks and Test Signals
Good signal for server-side token validation branches. It does not cover retry-on-transport-failure or malformed JSON/expiration.
