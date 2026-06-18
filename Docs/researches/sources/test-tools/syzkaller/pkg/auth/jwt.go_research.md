# sources/test-tools/syzkaller/pkg/auth/jwt.go

## Purpose
Retrieves and caches Google metadata-server identity JWTs for clients calling the syzkaller dashboard API.

## Important APIs, Types, and Functions
`DashboardAudience`, `expiringToken`, `extractJwtExpiration`, request function types, `retrieveJwtToken`, `TokenCache`, `MakeCache`, and `(*TokenCache).Get` form the API.

## Control Flow
`retrieveJwtToken` builds a metadata-server request with audience and `Metadata-Flavor: Google`, reads the token, checks HTTP status, extracts unverified `exp` from JWT payload, and returns token plus expiration. `MakeCache` fetches an initial token. `Get` locks, refreshes if expiration is less than one minute away, and returns an Authorization header value.

## State and Persistence Behavior
`TokenCache` stores one token in memory protected by a mutex. It performs network refreshes but no disk persistence.

## Dependencies and Integration Points
Used by syz-ci/syz-hub clients that need bearer credentials for dashboard API. Depends on metadata server JWT format and caller-injected request constructor/doer for testability.

## Risks and Test Signals
Risks include unverified expiration parsing, holding lock during HTTP refresh, and metadata-server availability. Tests in this subset focus on server-side auth, not this cache path.
