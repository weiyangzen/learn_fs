# sources/user-network-fs/rclone/backend/ftp/ftp.go

## Purpose
This file implements rclone's FTP/FTPS backend. It registers the `ftp` remote type, parses connection/security/proxy/encoding options, manages a pool of FTP control connections, and exposes the rclone `fs.Fs` and `fs.Object` operations for listing, upload, download, directory management, and server-side rename moves.

## Important APIs, Types, And Control Flow
The main exported types are `Options`, `Fs`, `Object`, and `FileInfo`. `NewFs` reveals the configured password or prompts when allowed, rejects simultaneous implicit and explicit TLS, initializes the connection pacer and optional concurrency token dispenser, dials once to validate credentials and discover FTP feature support, then handles the "root is a file" case by returning `fs.ErrorIsFile`.

Connection control is centered on `ftpConnection`, `getFtpConnection`, `putFtpConnection`, and `drainPool`. `ftpConnection` builds a `jlaffaye/ftp` dialer using rclone's HTTP dialer, optional SOCKS5 or HTTP CONNECT proxy logic, implicit/explicit TLS, EPSV/MLSD/UTF8/hidden-listing toggles, debug logging, and pacer retries. `getFtpConnection` consumes a token when `concurrency` is configured, reuses a pooled connection if possible, or opens a new connection. `putFtpConnection` validates potentially bad connections with `NOOP`, returns healthy connections to the pool, and resets the idle drain timer.

Object and directory operations use FTP commands through pooled connections. `findItem` prefers `MLST`/`GetEntry` when available, falls back to parent `LIST`, and normalizes names through the configured encoder. `List` runs `c.List` in a goroutine with a global timeout guard, then synthesizes rclone `Dir` and `Object` entries. `Put` recursively creates parent directories and calls `Object.Update`; `Update` uses `STOR`, optionally removes a partially uploaded file on failure, sets mtime, and refreshes metadata unless `no_check_upload` is enabled. `Open` supports seek/range reads via `RetrFrom` and wraps the response in `ftpReadCloser`, which returns or discards the connection during `Close`. `Move` and `DirMove` use `RNFR`/`RNTO` via `Rename`.

## State And Persistence
Runtime state is in the `Fs`: root, URL, credentials, TLS base config, connection pool, drain timer, pacer, feature flags, and feature-detection booleans for precise list times and MDTM/MFMT support. Persistent remote state is only FTP server state: directories, files, file mtimes, and renamed paths. The backend does not keep a local database. Pool state is cleaned by idle timeout or `Shutdown`.

## Dependencies And Integration Points
The implementation integrates `github.com/jlaffaye/ftp`, rclone's `fs` interfaces, `fshttp`, `pacer`, `accounting.LimitTPS`, `encoder.MultiEncoder`, proxy helpers, password obscuring, and rclone retry classification. It advertises `fs.Mover`, `fs.DirMover`, `fs.PutStreamer`, and `fs.Shutdowner`; hashes are unsupported.

## Risks And Test Signals
Major risks are FTP server variance: nonstandard MDTM writes, MLSD precision differences, LIST success for missing directories, unusual mkdir status codes, hidden-file listing behavior, TLS session resumption issues, proxy PASV address rewriting, and stuck data/control closes. Upload failure cleanup sleeps before deletion and can be fragile on slow servers. Tests should cover plain FTP, implicit and explicit FTPS, proxy paths, EPSV/MLSD/UTF8 toggles, low concurrency deadlock potential, range reads, close timeouts, directory marker behavior from LIST, and server-specific time precision.
