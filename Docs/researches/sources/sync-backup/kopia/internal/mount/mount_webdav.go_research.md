# sources/sync-backup/kopia/internal/mount/mount_webdav.go

Purpose: exposes a Kopia `fs.Directory` over a local WebDAV HTTP server and returns its URL as a mount path.

Important APIs/types/functions: `DirectoryWebDAV`, `webdavServerLogger`, `webdavController`, `Unmount`, `MountPath`, and `Done`.

Control flow: creates a `webdav.Handler` backed by `internal/webdavfs`, listens on loopback port `0`, serves HTTP in a goroutine, and returns a controller containing the server, listener URL, and done channel. Unmount calls `Shutdown`.

State and persistence behavior: process-local HTTP server and listener are active until shutdown; no repository state is mutated.

Dependencies and integration points: used directly on Windows before `net use` and on POSIX WebDAV fallback; integrates `golang.org/x/net/webdav`, `net/http`, and `fs.Directory`.

Risks and test signals: local server lifecycle and shutdown races are key. Tests should verify URL formation, error logging, server shutdown, and read-only WebDAV behavior.
