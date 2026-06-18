# sources/user-network-fs/rclone/lib/rest/url_test.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/rest/url_test.go -->
## sources/user-network-fs/rclone/lib/rest/url_test.go

Purpose: validates URL joining and escaping helpers against expected URL strings.

Important APIs and control flow: `TestURLJoin` table-tests base/path combinations, including relative paths, parent directories, absolute paths, absolute URLs, percent characters, and colon parsing. `TestURLPathEscape` checks path escaping quirks. `TestURLPathEscapeAll` verifies RFC-unreserved characters remain literal while spaces, colon, percent, dollar, question mark, and UTF-8 umlaut bytes are percent-encoded.

State, dependencies, and integration: dependencies are `fmt`, `net/url`, `testing`, and testify.

Risks and test signals: good coverage for expected escaping behavior. It does not test invalid percent escape sequences beyond the colon parse case.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/rest/url_test.go -->
