# sources/object-store/minio/cmd/jwt_test.go

## Purpose

`jwt_test.go` tests metrics/web request JWT authentication for root credentials and benchmarks standard-claims parsing, map-claims parsing, node-token signing, and cached token retrieval.

## Important Tests And Control Flow

`getTokenString` creates a one-day HS512 token with MinIO map claims and an access key. `TestWebRequestAuthenticate` prepares a filesystem-backed test object layer, initializes global test config, signs a token with `globalActiveCred`, and checks three request cases: valid Authorization header succeeds, missing Authorization returns `errNoAuthToken`, and malformed token returns `errAuthentication`.

`BenchmarkParseJWTStandardClaims` signs an inter-node token with `authenticateNode` and repeatedly parses it with `xjwt.ParseWithStandardClaims`. `BenchmarkParseJWTMapClaims` parses the same token through `xjwt.ParseWithClaims` and a callback returning the secret key. `BenchmarkAuthenticateNode` compares repeatedly signing a new node token with reading the cached global token closure returned by `newCachedAuthToken`.

## State, Dependencies, Integration, Risks, And Signals

The test mutates global MinIO test configuration through `prepareFS` and `newTestConfig`, then uses global active credentials. It directly validates the root-token success path and high-level error mapping for missing/malformed headers. Gaps include disabled users, non-root IAM users, expired temporary credentials, root-access-disabled behavior, embedded claim copying, groups/owner return values, and invalid signing-key paths. The benchmarks indicate performance sensitivity around JWT parsing/signing and justify the cached node-token closure.
