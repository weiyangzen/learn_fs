<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/webdav/webdav_test.go -->
# sources/user-network-fs/rclone/cmd/serve/webdav/webdav_test.go

Source read: complete file, 354 lines, 9009 bytes, sha256 `6095bc47dc506979bb4bcaef7bab133733403535ee9b7d35abe3354011348ea1`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/webdav/webdav_test.go_research.md`.

## Purpose
Tests serve webdav through backend integration, HTTP directory/file behavior, compression, range handling, and rc startup.

## Important APIs, types, and functions
`TestWebDav`, `TestHTTPFunction`, `HelpTestGET`, `startAuthenticatedServer`, compression tests, range test, and `TestRc` are the main tests. Interface assertions validate `FileInfo` WebDAV extensions.

## Control flow
Tests start local-backed WebDAV servers with auth/template/BaseURL/hash options, run generic backend tests, compare HTTP responses to golden files, and inspect gzip/range behavior with real HTTP clients.

## State and persistence behavior
State includes temporary server listeners, configured filter rules, golden files optionally rewritten by `-updategolden`, and local testdata files.

## Dependencies and integration points
Depends on local backend, servetest, filter config, gzip, net/http, WebDAV backend, templates, obscure passwords, and rc.

## Risks and edge cases
Build-tagged away on Windows and Darwin due troublesome character mappings. Golden tests are sensitive to template/output formatting. `-updategolden` writes fixture files when requested.

## Test signals
Strong signal for WebDAV protocol conformance, browser-style directory listing, auth, ETag/hash config, gzip middleware, and range safety.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/webdav/webdav_test.go -->
