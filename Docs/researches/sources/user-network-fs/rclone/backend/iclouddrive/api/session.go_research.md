<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/api/session.go -->
## Research: sources/user-network-fs/rclone/backend/iclouddrive/api/session.go

### Purpose
`session.go` implements Apple's iCloud session lifecycle. It manages cookies, Apple auth headers, SRP sign-in, 2FA push and SMS verification, trust-token exchange, session validation, Advanced Data Protection PCS cookie acquisition, and request header construction for both setup and idmsa endpoints.

### Important APIs, Types, and Functions
`Session` stores session token, `scnt`, session ID, account country, trust token, client ID, auth attributes, frame ID, cookies, account info, a mutex, REST client, and a `needs2FA` flag. `SignIn` orchestrates SRP auth through `authStart`, `authFederate`, `authSRPInit`, and `authSRPComplete`. `AuthWithToken`, `ValidateSession`, `TrustSession`, `RequestPushNotification`, `Validate2FACode`, `GetAuthState`, `RequestSMSCode`, and `ValidateSMSCode` cover post-SRP account login and 2FA flows.

Cookie and debug helpers include `mergeCookies`, `extractHeaders`, `GetCookieString`, `cookieValueFingerprint`, `authStateBodySummary`, `cookieDebugSummary`, `cookieDebugSummaries`, and `cookieJarDebugSummaries`. ADP helpers include `ensurePCSCookies`, `acquirePCSCookiesFor`, `pcsServices`, and `hasPCSCookiesFor`. Header helpers include `getSRPAuthHeaders`, `GetAuthHeaders`, `GetHeaders`, and `GetCommonHeaders`.

### Control Flow
`SignIn` starts an OAuth-like idmsa auth session, federates the Apple ID, creates an SRP client, sends public value `A`, decodes server salt and `B`, derives the password key, computes proofs, and completes sign-in. `authSRPComplete` treats HTTP 200 as success, 409 as 2FA required, 412 as a repair flow, 403 as invalid credentials, and other statuses as hard errors.

For 2FA, push validation posts a security code then trusts the session and calls `AuthWithToken`. SMS flow first retrieves auth state, optionally unwraps `phoneNumberVerification`, handles singular phone fallback, requests an SMS code, validates it, trusts the session, and logs into setup. `Request` wraps JSON REST calls and extracts cookies/session headers after successful calls. PCS acquisition polls `/requestPCS` every 10 seconds up to 30 attempts and verifies expected PCS cookies are present after a success response.

### State and Persistence
This file mutates only in-memory `Session` state; callers persist cookies, trust token, and selected auth state. `extractHeaders` updates cookies, account country, session ID, session token, trust token, scnt, and auth attributes from response headers. `mergeCookies` replaces cookies by name and removes existing cookies when Apple sends empty-value tombstones. `NewSession` creates a UUID frame ID and installs a request filter that forces the Safari-like iCloud user agent.

### Dependencies and Integration Points
The session layer depends on `srp.go` for SRP math, `Client.Authenticate` in `client.go`, backend config flow in `icloud.go`, rclone `fshttp` and `rest`, and Apple's `idmsa.apple.com/appleauth/auth` and setup webservice endpoints. It provides the cookie/header source for Drive and Photos requests.

### Risks and Edge Cases
The code is sensitive to Apple's private auth protocol, headers, status codes, and response nesting. Cookie handling must process tombstones correctly or stale 2FA/PCS cookies can poison later requests. PCS polling can block for up to five minutes and requires user approval. Debug helpers intentionally fingerprint rather than log secrets, which reduces leakage risk. `Session.Request` only extracts headers after no transport/error return; auth failure paths use direct calls where needed to capture response bodies and headers.

### Test Signals
`session_test.go` directly verifies cookie merging and empty-cookie deletion. Other behavior is indirectly exercised by config flows and Photos/Client tests. SRP cryptographic behavior is covered separately in `srp_test.go`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/api/session.go -->
