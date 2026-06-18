<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/restic.go -->
# sources/user-network-fs/rclone/cmd/serve/restic/restic.go

Source read: complete file, 572 lines, 16585 bytes, sha256 `51f13038acf0109b22c63c6dfe9a2d0b764ad00d44055ce798b1ffa1dc6e5922`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/restic/restic.go_research.md`.

## Purpose
Implements `rclone serve restic`, an HTTP or HTTP/2-over-stdio server exposing an rclone remote through restic's REST backend API.

## Important APIs, types, and functions
`Options` combines HTTP/auth config with `Stdio`, `AppendOnly`, `PrivateRepos`, and `CacheObjects`. `Command`, `newServer`, `server.Bind`, `WithRemote`, `checkPrivate`, `serveObject`, `postObject`, `deleteObject`, `listObjects`, and `createRepo` are the central APIs. `ContextRemoteKey` carries the translated remote path.

## Control flow
Command startup builds an Fs, creates a server, and either serves HTTP listeners or binds an HTTP/2 server to `StdioConn`. Requests flow through `WithRemote`, which trims URL paths and maps restic `data/<hash>` objects into `data/<prefix>/<hash>`. GET/HEAD serve objects, POST creates repositories or writes objects, DELETE removes objects, and list endpoints require the restic v2 Accept header.

## State and persistence behavior
Repository state is ordinary directories and objects on the backing Fs. Local state includes the HTTP server, optional object cache, request context values, and append-only/private-repo options. Append-only blocks overwrites and most deletes except lock files. Private repos restrict paths to the authenticated username prefix.

## Dependencies and integration points
Depends on chi, rclone `lib/http`, HTTP auth, VFS-independent `fs` operations, `operations.RcatSize`, `walk.ListR`, systemd notification, terminal checks, and `x/net/http2` for stdio mode. Registered both as Cobra command and rc serve type.

## Risks and edge cases
Security depends on correct auth configuration and `checkPrivate` path matching. Append-only mode still allows lock deletion by path pattern. Cache entries can go stale after external mutation. `WithRemote` path rewriting must remain compatible with restic's expected data layout.

## Test signals
`restic_test.go`, append-only/private-repos tests, cache tests, and optional upstream restic integration tests cover path mapping, HTTP errors, overwrite/delete restrictions, private repository auth, rc start, and object cache behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/restic.go -->
