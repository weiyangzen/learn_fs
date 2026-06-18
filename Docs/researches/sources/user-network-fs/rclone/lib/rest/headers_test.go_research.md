# sources/user-network-fs/rclone/lib/rest/headers_test.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/rest/headers_test.go -->
## sources/user-network-fs/rclone/lib/rest/headers_test.go

Purpose: table-tests `ParseSizeFromHeaders`.

Important APIs and control flow: `TestParseSizeFromHeaders` builds headers with optional `Content-Length` and `Content-Range` values and asserts the returned full size or `-1`.

State, dependencies, and integration: dependencies are `net/http`, `testing`, and testify. It uses a compact table covering absent headers, valid length, invalid range, valid range overriding content length, unsupported units, wildcard total, and unsatisfied-range form.

Risks and test signals: the test confirms intended precedence and failure behavior. It does not test malformed numbers beyond wildcard or missing slash cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/rest/headers_test.go -->
