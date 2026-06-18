<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/api/session_test.go -->
## Research: sources/user-network-fs/rclone/backend/iclouddrive/api/session_test.go

### Purpose
`session_test.go` is a focused regression test for `Session.extractHeaders` and cookie management. It verifies that Apple response headers update session state and that Set-Cookie tombstones remove stale cookies instead of leaving empty cookie values in the jar.

### Important APIs, Types, and Functions
The tests construct `Session` values through `NewSession`, populate `Session.Cookies`, build synthetic `http.Response` objects with `Set-Cookie` and `X-Apple-Session-Token` headers, and call the package-private `extractHeaders` method. Assertions inspect `Session.Cookies`, `Session.SessionToken`, and `GetCookieString`.

### Control Flow
`TestExtractHeadersMergesCookies` starts with one cookie, sends an updated cookie with the same name and a new cookie, and checks that the existing entry is replaced and the new entry is appended. It also verifies that `X-Apple-Session-Token` is captured. `TestExtractHeadersDeletesEmptyCookies` starts with an HSA login cookie and a normal cookie, sends an empty-value Set-Cookie for the HSA login cookie, and expects only the normal cookie to remain.

### State and Persistence
The tests manipulate only in-memory session state. They validate the invariant that `GetCookieString` skips empty cookies because those cookies should have been removed by `mergeCookies` where possible.

### Dependencies and Integration Points
This file depends only on `net/http`, `testing`, and `testify`. It protects behavior used by the SRP/2FA config flow and all subsequent Drive/Photos requests that reuse session cookies.

### Risks and Edge Cases
Apple auth flows frequently set cookies with the same names or empty values to clear state. If merge semantics regress, stale 2FA cookies can remain, new auth cookies may not replace old values, and serialized cookie strings can become invalid. These tests do not cover domain/path-sensitive duplicate cookies; merge is name-only.

### Test Signals
The tests are small but high signal for a previous class of session persistence bugs. They should run quickly and deterministically in unit test suites.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/api/session_test.go -->
