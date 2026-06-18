# sources/user-network-fs/rclone/lib/jwtutil/jwtutil.go

Source read signal: reviewed complete local file (115 lines, sha256 8f3d3c369eb3111c).

Purpose: Implements JWT bearer-token authentication helpers for rclone backends that exchange signed JWTs for OAuth tokens.

Important APIs/types/functions: Exports `RandomHex` and `Config`; helper `bodyToString`; private JSON `response` struct.

Control flow: `RandomHex` returns hex-encoded crypto-random bytes. `Config` signs supplied JWT claims with RS256 and custom headers, posts an `application/x-www-form-urlencoded` JWT bearer grant to the token URL with query params, logs/reads the body, validates HTTP 200 and access token presence, builds an `oauth2.Token` with optional expiry, and stores it through `oauthutil.PutToken`.

State and persistence behavior: Persists the resulting OAuth token into the supplied config mapper. Reads randomness and performs an outbound HTTP request through the provided client.

Dependencies and integration points: Uses `golang-jwt/jwt/v4`, RSA keys, `oauth2`, rclone config maps, and `oauthutil`. Backends can call this during config to avoid browser OAuth flows.

Risks and test signals: Response body close is deferred after reading; the deferred error formatting currently wraps the outer `err` rather than the close error. Non-200 responses return only status, though body is logged at debug. Tests should mock token endpoints and malformed JSON.
