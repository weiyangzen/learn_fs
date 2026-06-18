# sources/user-network-fs/rclone/lib/http/server_test.go

Source read signal: reviewed complete local file (604 lines, sha256 30f6d4132d490005).

Purpose: End-to-end tests for the reusable HTTP server wrapper.

Important APIs/types/functions: Provides test helpers `testEmptyHandler`, `testEchoHandler`, `testAuthUserHandler`, `testExpectRespBody`, `testGetServerURL`, `testNewHTTPClientUnix`, and `testReadTestdataFile`; tests Unix sockets, HTTP auth, base URL normalization, TLS/mTLS config, h2c, and help text.

Control flow: Tests create `Server` instances with temp addresses or sockets, mount handlers, call `Serve`, make real client requests, assert responses, then call `Shutdown`.

State and persistence behavior: Creates Unix socket files and local TCP listeners; reads TLS testdata; cleanup is via deferred shutdown and temp dirs.

Dependencies and integration points: Uses `net/http`, `crypto/tls`, `x/net/http2`, and `testify/require`. Exercises integration across `server.go`, middleware, auth, TLS, and context helpers.

Risks and test signals: Strong coverage for TLS misconfiguration and listener URL generation. Some tests skip certificate hostname validation with `InsecureSkipVerify` because fixtures lack proper SANs.
