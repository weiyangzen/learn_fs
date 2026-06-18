# sources/user-network-fs/rclone/lib/rest/headers.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/rest/headers.go -->
## sources/user-network-fs/rclone/lib/rest/headers.go

Purpose: extracts full object size from HTTP response headers.

Important APIs and control flow: `ParseSizeFromHeaders(headers)` defaults to `-1`. It first parses `Content-Length` when present. It then checks `Content-Range`; if absent, the content length result is returned. When `Content-Range` is present, it must start with `bytes ` and contain `/`; the value after slash is parsed and returned as the full size. Invalid data returns `-1`.

State, dependencies, and integration: stateless helper depending on `net/http`, `strconv`, and `strings`. It integrates with REST backends that need to infer total object size from range responses or normal responses.

Risks and test signals: wildcard total sizes such as `bytes 0-1/*` return `-1`. The parser does not validate the left-hand byte range, only the unit and total. Tests cover content length, valid/invalid content range, unit mismatch, wildcard totals, and `bytes */size`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/rest/headers.go -->
