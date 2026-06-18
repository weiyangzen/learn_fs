<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/proxy/proxy_code.go -->
# sources/user-network-fs/rclone/cmd/serve/proxy/proxy_code.go

Source read: complete file, 41 lines, 613 bytes, sha256 `7cb98b6d26b97a00b617e4cecbaddda33ceeb8f526e4dd39d82bfe4d290c90e0`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/proxy/proxy_code.go_research.md`.

## Purpose
Provides a build-ignored test auth proxy executable. It reads the proxy protocol JSON from stdin and emits a local backend config suitable for unit tests.

## Important APIs, types, and functions
`main` decodes a `map[string]string`, mutates `user` by appending `-test`, treats an `error` input as fatal, defaults `type` to `local`, defaults `_root` to empty, and writes JSON to stdout.

## Control flow
The test process is launched by `go run`; stdin drives the output config and stdout becomes the config map parsed by `proxy.run`.

## State and persistence behavior
No persistent state. It only transforms one request and exits. Its output may include password/public-key fields from input for proxy cache and obscuring tests.

## Dependencies and integration points
Depends only on standard JSON/log/os packages and the proxy JSON contract from `proxy.go`.

## Risks and edge cases
Because it is build-ignored, it is only valid when explicitly invoked with `go run`. It is intentionally permissive and should not be copied as a production auth proxy.

## Test signals
`proxy_test.go` uses it to validate normal proxy operation, command failure, and obscuring behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/proxy/proxy_code.go -->
