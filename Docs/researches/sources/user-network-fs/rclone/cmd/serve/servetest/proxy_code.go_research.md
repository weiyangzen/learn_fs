<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/servetest/proxy_code.go -->
# sources/user-network-fs/rclone/cmd/serve/servetest/proxy_code.go

Source read: complete file, 35 lines, 554 bytes, sha256 `a87f5eabd427ca106a5c83aca90045852a3c46124f7ab643c6352d38defd1318`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/servetest/proxy_code.go_research.md`.

## Purpose
Build-ignored auth proxy helper used by serve protocol integration tests.

## Important APIs, types, and functions
`main` expects a root path argument, decodes input JSON, and emits a local backend config with `_root` set to that root and `_obscure` set to `pass`.

## Control flow
Servetest invokes it via `go run` when exercising auth-proxy mode for local-backed protocol tests.

## State and persistence behavior
No persistent state; one request in, one config out.

## Dependencies and integration points
Depends only on standard JSON/log/os packages and the proxy JSON contract.

## Risks and edge cases
Hardcodes `type=local`, so `servetest.RunWithBackend` disables auth-proxy mode for non-local backing remotes.

## Test signals
Used by SFTP, WebDAV, and S3 serve integration tests through `servetest`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/servetest/proxy_code.go -->
