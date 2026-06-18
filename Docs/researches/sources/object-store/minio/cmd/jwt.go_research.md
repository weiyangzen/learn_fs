# sources/object-store/minio/cmd/jwt.go

## Purpose

`jwt.go` contains JWT helpers for node authentication and metrics/web request authentication. It signs long-lived inter-node tokens, validates bearer tokens against root or IAM user secrets, merges embedded credential claims, and reports owner/group information for authorization decisions.

## Important APIs, Types, And Control Flow

Constants define the bearer algorithm label, one-day default web JWT expiry, and roughly 100-year inter-node token expiry. Package errors distinguish missing tokens, invalid access keys, disabled keys, authentication failure, skew, and malformed auth. `authenticateNode(accessKey, secretKey)` builds MinIO standard claims with access key and long expiry, then signs with HS512.

`metricsRequestAuthenticate(req)` extracts a token from the Authorization header using `jwt/v4/request`, parses it into MinIO `MapClaims`, and chooses the signing key by access key. Non-root users are looked up through `globalIAMSys.GetUser`; disabled or expired credentials are rejected. Root credentials are allowed only when `globalAPIConfig.permitRootAccess()` permits them. After successful parsing, non-root users are looked up again, embedded claims from `checkClaimsFromToken` are copied into the parsed claims, root-derived credentials can be disabled when root access is disabled, owner status is computed based on session policy and parent user, and credential groups are returned. `newCachedAuthToken` returns a closure over `globalNodeAuthToken`.

## State, Dependencies, Integration, Risks, And Tests

State is global: active root credentials, IAM cache, API root-access config, and node auth token. Dependencies include `golang-jwt/jwt/v4`, MinIO auth/JWT packages, and policy session claim names. Integration points include metrics endpoints, inter-node calls, and code paths needing cached node bearer tokens. Risks include intentionally collapsed parse errors into `errAuthentication`, reliance on global root-access state, duplicate user lookup with possible cache changes between lookups, owner semantics when session policies are present, and token lifetime for inter-node auth. `jwt_test.go` covers valid, missing, and invalid metric tokens plus benchmarks for parsing and cached token access.
