# sources/user-network-fs/rclone/backend/webdav/webdav_internal_test.go

Purpose: local HTTP-server tests for WebDAV internals.

Important APIs: `prepareServer`, `prepare`, `TestHeaders`, `TestListAllAuthRedirect`, and `TestReservedCharactersInPathAreEscaped`.

Control flow/state: a test server validates custom headers and returns quota XML; redirect test verifies `auth_redirect` preserves Authorization across cross-host redirect; reserved-character test captures URI and checks semicolon escaping.

Dependencies/integration: `httptest`, config helpers, `obscure`, rclone `fs`, webdav package, and testify.

Risks/test signals: fast local coverage for custom headers, explicit auth forwarding, and RFC3986 path escaping.
