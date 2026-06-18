<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/proxy/proxy_test.go -->
# sources/user-network-fs/rclone/cmd/serve/proxy/proxy_test.go

Source read: complete file, 269 lines, 8188 bytes, sha256 `42463bf162b44d32ce03fc0bf01ddfb5d1c709e6963683cde7f4dc2575174b15`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/proxy/proxy_test.go_research.md`.

## Purpose
Tests the auth proxy implementation from helper process invocation through VFS cache behavior for password and public-key authentication.

## Important APIs, types, and functions
`TestRun` covers `Proxy.run` success, failure, and `_obscure`. Later subtests call `Proxy.call`, `Proxy.Call`, and `Proxy.Get` with password and public-key inputs and verify cache keys, VFS creation, and credential mismatch behavior.

## Control flow
The tests build absolute paths to `proxy_code.go`, execute it with `go run`, inspect returned config values, then instantiate `Proxy` with local backend/VFS options. They call the proxy directly and through the cache-facing API.

## State and persistence behavior
State is test-local except for temporary VFS cache entries inside each `Proxy`. It validates that a changed credential gets a different cache path and does not reuse stale VFS state.

## Dependencies and integration points
Depends on the local backend, `configmap`, `obscure`, `vfscommon`, testify assertions, and the ignored helper source.

## Risks and edge cases
Tests manipulate executable paths and process execution, so failures can reflect missing Go toolchain or working-directory assumptions. Coverage is focused on local backend behavior and does not validate production helper security.

## Test signals
Strong test signal for JSON protocol handling, field obscuring, password/public-key cache segregation, and retrieval through cache keys.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/proxy/proxy_test.go -->
