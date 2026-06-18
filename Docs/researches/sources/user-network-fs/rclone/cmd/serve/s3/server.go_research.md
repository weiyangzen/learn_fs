<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/server.go -->
# sources/user-network-fs/rclone/cmd/serve/s3/server.go

Source read: complete file, 222 lines, 5230 bytes, sha256 `8db95539e9f15ff840ed77e945ef150e8d060381e79598d506f84ed98e3389c3`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/s3/server.go_research.md`.

## Purpose
Constructs and runs the HTTP S3 server around `gofakes3`, rclone VFS, optional auth proxy, and HTTP listener configuration.

## Important APIs, types, and functions
`Server` stores HTTP server, options, Fs, VFS/proxy, gofakes3 instance, handler, secret, and ETag hash type. `newServer`, `getVFS`, `auth`, `Bind`, `Serve`, `Addr`, `Shutdown`, auth middlewares, `parseAccessKeyID`, `stringToMd5Hash`, and `getAuthSecret` are the key functions.

## Control flow
`newServer` selects ETag hash behavior, parses auth key pairs, builds gofakes3 with v4 auth and integrity checks, then either creates a fixed VFS or wraps the handler with proxy auth middleware. HTTP server routes all paths to the gofakes3 handler. Proxy mode extracts the access key ID from SigV4, calls the auth proxy, stores the VFS in request context, and adds a temporary auth key pair.

## State and persistence behavior
State includes the HTTP listener, one fixed VFS or per-auth proxy VFS cache, gofakes3 auth key registry, and request context values. The proxy path uses MD5(accessKeyID) as proxy username and accessKeyID as password input.

## Dependencies and integration points
Depends on chi, gofakes3, signature parsing, rclone HTTP server, VFS, proxy, hashes, and auth utilities in `utils.go`.

## Risks and edge cases
Anonymous access is allowed if no auth keys are provided. Proxy auth still adds auth keys dynamically and must parse Authorization correctly. `getAuthSecret` uses only the first auth pair secret. Adding auth keys per request may accumulate state in gofakes3.

## Test signals
S3 integration tests exercise fixed auth, proxy auth, rc startup, and real client behavior through this server.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/server.go -->
