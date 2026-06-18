<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/sftp/connection.go -->
# sources/user-network-fs/rclone/cmd/serve/sftp/connection.go

Source read: complete file, 385 lines, 10618 bytes, sha256 `26f6d68eb5bca3b87786a96138e87250ed1c77ad98b2323a253e3a994663f3dc`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/sftp/connection.go_research.md`.

## Purpose
Handles per-SSH-connection channel requests for serve sftp, including SFTP subsystem service and a constrained exec command surface for rclone compatibility.

## Important APIs, types, and functions
`describeConn`, `shellUnEscape`, `conn`, `execCommand`, `handleHashsumCommand`, `handleChannel`, `handleChannels`, `serveChannel`, `serveStdio`, and `stdioChannel` implement session behavior.

## Control flow
After SSH authentication, each session channel waits for either `subsystem sftp` or `exec`. SFTP sessions are served by `pkg/sftp.NewRequestServer`. Exec supports `df`, several hashsum commands, `rclone hashsum`, limited `xxhsum -H2`, and legacy `echo 'abc' | md5sum/sha1sum` probes, then sends an exit-status request.

## State and persistence behavior
Connection state is the selected VFS, SFTP handlers, and descriptive logging string. Stdio mode adapts stdin/stdout to an SFTP channel without SSH handshake.

## Dependencies and integration points
Depends on `pkg/sftp`, `x/crypto/ssh`, rclone hashes, VFS, terminal checks, and stdio files.

## Risks and edge cases
Exec parsing is intentionally limited and string-based; unsupported commands fail. Hashing an uploading VFS node may read cached file contents. Channel goroutines can block if clients open sessions without sending recognized requests.

## Test signals
`connection_test.go` covers shell unescaping. SFTP backend integration and handler tests exercise subsystem behavior and hash/stat interactions indirectly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/sftp/connection.go -->
