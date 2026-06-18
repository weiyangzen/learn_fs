# sources/sync-backup/kopia/repo/blob/sftp/sftp_storage.go

Purpose: implements a sharded Kopia `blob.Storage` provider on top of SFTP, supporting internal SSH, external SSH subprocesses, reconnects, capacity, atomic temp-file writes, host-key verification, and credential handling.

Important APIs/types/functions: `sftpStorage` embeds `sharded.Storage`; `sftpImpl` implements sharded `Impl`; `sftpConnection` wraps an SFTP client and close function. Core methods are `GetBlobFromPath`, `GetMetadataFromPath`, `PutBlobInPath`, `DeleteBlobInPath`, `ReadDir`, `GetCapacity`, `ConnectionInfo`, `DisplayName`, and `Close`. Setup helpers include `getHostKeyCallback`, `getSigner`, `createSSHConfig`, `getSFTPClientExternal`, `getSFTPClient`, and `New`.

Control flow: `New` creates a sharded storage, attaches a reconnecting connection manager, opens a connection without the caller's cancellation, ensures the remote root exists, and returns a retrying wrapper. Reads open files, stream whole or ranged content, seek for partial reads, and enforce exact length. Writes copy potentially fragmented `blob.Bytes` into a contiguous buffer, create a random temp file and missing directories, write/close it, atomically `PosixRename` it into place, and optionally set or return modtime.

State and persistence behavior: remote blobs are stored by the shared sharded layout beneath `Options.Path`; writes are staged as `*.tmp.<random>` and become visible only after rename. `.shards` may be persisted by the sharded layer. Active SSH/SFTP connection state is held in the reconnecter and closed by provider `Close`.

Dependencies/integration: integrates `github.com/pkg/sftp`, `x/crypto/ssh`, knownhosts, `internal/connection`, `dirutil`, `sharded`, and `retrying`. It maps not-found and connection-lost conditions to blob or reconnect semantics.

Risks and edge cases: error detection for not-exist includes string matching. External SSH argument splitting is simple whitespace splitting. Temporary known-hosts data touches disk briefly. `DoNotRecreate` and retention are unsupported. Atomicity depends on server support for `PosixRename`.

Test signals: SFTP tests launch an `atmoz/sftp` Docker server, validate key/password auth, embedded credentials, provider validation, canceled-constructor context reuse, invalid host fast failure, and rejection of relative key/known-hosts files.
