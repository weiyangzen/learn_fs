# sources/user-network-fs/rclone/lib/http/middleware_test.go

Source read signal: reviewed complete local file (648 lines, sha256 c6b3982827b6cdda).

Purpose: Integration-tests HTTP authentication and middleware behavior through live `Server` instances.

Important APIs/types/functions: Tests include `TestMiddlewareAuth`, `TestMiddlewareAuthCertificateUser`, `TestMiddlewareCORS`, `TestMiddlewareCORSEmptyOrigin`, `TestMiddlewareCORSWithAuth`, and `TestMiddlewareResponseHeaders`.

Control flow: Tests create temporary servers with different `Config` and `AuthConfig`, mount echo or username handlers, issue real HTTP(S) requests, and assert status, body, auth challenge headers, CORS headers, and response headers.

State and persistence behavior: Starts local listeners and shuts them down after each case. Reads test TLS certs and htpasswd files.

Dependencies and integration points: Uses `net/http`, `crypto/tls`, `context`, server helpers from `server_test.go`, and `testify/require`. It validates interaction among `server.go`, `auth.go`, `context.go`, and middleware.

Risks and test signals: Strong signal for authentication precedence, invalid header usernames, cert common-name extraction, and `OPTIONS` preflight bypass. It does not test spoofed proxy chains beyond username validation.
