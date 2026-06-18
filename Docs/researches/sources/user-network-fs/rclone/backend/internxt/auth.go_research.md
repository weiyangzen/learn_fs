# sources/user-network-fs/rclone/backend/internxt/auth.go

## Purpose
Implements Internxt authentication support: user metadata retrieval, JWT expiry parsing, OAuth token conversion/persistence, Basic auth derivation for bucket operations, token refresh, fallback relogin, and serialized re-authorization after 401 responses.

## Important APIs, Types, and Functions
`userInfo` stores root folder ID, bucket, bridge user, and user ID. `userInfoConfig` carries a token. Functions include `getUserInfo`, `parseJWTExpiry`, `jwtToOAuth2Token`, `computeBasicAuthHeader`, `refreshJWTToken`, `Fs.reLogin`, `Fs.refreshOrReLogin`, and `Fs.reAuthorize`.

## Control Flow
`getUserInfo` calls Internxt's refresh endpoint and validates required user fields. JWT conversion parses claims without validation to extract `exp`. `refreshJWTToken` loads the current rclone OAuth token, calls the refresh endpoint, parses the new JWT, saves it, and persists bucket if present.

`refreshOrReLogin` first attempts refresh. On non-401 errors it returns the refresh error. On 401 it decrypts the stored password, checks whether 2FA is required, performs a full login if possible, saves the new token, and refreshes config fields. `reAuthorize` serializes this path with `authMu` and sets `authFailed` as a circuit breaker after permanent failure.

## State and Persistence
Tokens are persisted through `oauthutil.PutToken` in the rclone config mapper. Bucket may be stored in config. In-memory `Fs` state updates include `cfg.Token`, `cfg.BasicAuthHeader`, bridge user, user ID, bucket, and root folder ID. `authFailed` prevents repeated failing reauth loops.

## Dependencies and Integration Points
Uses `github.com/internxt/rclone-adapter/auth` and config/errors packages, `golang-jwt/jwt/v5`, rclone `configmap`, `obscure`, `fserrors`, `fshttp`, and `oauthutil`. Called by `NewFs`, token renewer callbacks, and retry handling in `internxt.go`.

## Risks and Edge Cases
JWT parsing is unverified and only used for expiry extraction; malformed or missing `exp` prevents token storage. Re-login cannot proceed for 2FA accounts and requires users to reconnect. Once `authFailed` is set, subsequent 401 handling fails permanently for that `Fs`. `refreshOrReLogin` recomputes Basic auth using existing bridge/user values after refresh; if refresh changes those fields but they are not separately loaded, there is a consistency risk.

## Test Signals
No local unit tests cover token parsing, Basic auth derivation, refresh/relogin fallback, or circuit breaker behavior. Integration tests exercise auth only against real Internxt accounts.
