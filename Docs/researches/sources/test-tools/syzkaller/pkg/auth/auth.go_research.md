# sources/test-tools/syzkaller/pkg/auth/auth.go

## Purpose
Validates Google OAuth2 identity tokens for dashboard API clients and maps them to syzkaller auth subjects.

## Important APIs, Types, and Functions
Constants `GoogleTokenInfoEndpoint` and `OauthMagic`, `Endpoint`, `MakeEndpoint`, `jwtClaimsParse`, `jwtClaims`, `queryTokenInfo`, and `DetermineAuthSubj` are the core API.

## Control Flow
`DetermineAuthSubj` ignores missing/non-Bearer headers for password auth fallback. Bearer tokens are posted to tokeninfo with up to three HTTP attempts, JSON claims are parsed, audience is checked against `DashboardAudience`, expiration is compared with `now`, and the subject is returned with `OauthMagic` prefix.

## State and Persistence Behavior
No cache in this endpoint path; every bearer verification queries the endpoint. No persistence.

## Dependencies and Integration Points
Depends on net/http, tokeninfo protocol, and `DashboardAudience` from `jwt.go`. Used by dashboard/API authentication.

## Risks and Test Signals
Risks include no response timeout at this layer, strict single-header behavior, and trusting tokeninfo availability. Tests cover valid bearer, wrong audience, expired token, missing/bad headers, and bad HTTP status.
