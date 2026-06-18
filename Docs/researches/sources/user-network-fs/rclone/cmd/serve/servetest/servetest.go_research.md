<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/servetest/servetest.go -->
# sources/user-network-fs/rclone/cmd/serve/servetest/servetest.go

Source read: complete file, 165 lines, 4968 bytes, sha256 `b9a1e82cd3fcd4dcf9ec8fc3a39327b1870ecbf0d292a49e897ecc0dcdaded44`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/servetest/servetest.go_research.md`.

## Purpose
Shared integration harness for testing `rclone serve <protocol>` looped back into rclone backend integration tests.

## Important APIs, types, and functions
`StartFn`, `Run`, `RunWithBackend`, internal `run`, and `makeBackingFs` create a backing Fs, start the server, export backend config through environment variables, and execute the matching backend package's `go test`.

## Control flow
Normal mode passes a real Fs to the server. Auth-proxy mode passes nil and sets `proxy.Opt.AuthProxy` to `go run proxy_code.go <root>`. For named backing remotes, it starts the matching testserver and uses a random subremote.

## State and persistence behavior
State includes temporary/backing remote data, process cwd changes into backend package directories, environment variables for generated remote config, and temporary mutation of global proxy options.

## Dependencies and integration points
Depends on fstest, testserver, os/exec, configmap, proxy package, and backend integration test conventions.

## Risks and edge cases
Not parallel-safe around cwd and global proxy option mutation. Backend test failures can be caused by the served protocol, the client backend, or the backing remote.

## Test signals
Central test signal for protocol servers because SFTP, WebDAV, and S3 use it for generic backend conformance.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/servetest/servetest.go -->
