# sources/user-network-fs/rclone/backend/smb/connpool.go

## Purpose

`connpool.go` manages SMB TCP sessions and mounted shares for the SMB backend. It amortizes authentication and share mounting across operations and drains idle connections safely.

## Important APIs, Types, and Functions

`conn` wraps a network connection pointer, `go-smb2` session, mounted share, and share name. `Fs.dial` creates NTLM or Kerberos initiators and establishes an SMB session. `newConnection` dials and optionally mounts a share. `conn.mountShare` switches mounted shares. `getConnection` retrieves or opens a connection. `putConnection` returns a connection to the pool or closes it if unhealthy. `drainPool` closes pooled connections when no active sessions remain. `addSession`, `removeSession`, and `getSessions` track active readers/writers.

## Control Flow

Operations call `getConnection` with a share name. The pool is searched under lock; each candidate is remounted to the requested share and discarded if remount fails. If none is usable, a new connection is opened through the pacer. On return, `putConnection` probes the session with `Echo` after non-routine errors and only pools healthy sessions. The idle timer nudges `drainPool`, which refuses to close idle connections while active sessions exist and otherwise closes pooled sessions in an `errgroup`.

## State and Persistence Behavior

State is in-memory only: `Fs.pool`, `poolMu`, active session count, mounted share per connection, and idle timer. Credentials come from config and Kerberos caches but are not persisted here.

## Dependencies and Integration Points

It depends on `cloudsoda/go-smb2`, rclone accounting TPS limiting, `fshttp` dialers, obscure password reveal, and `kerberos.go` when Kerberos is enabled. `smb.go` object/list/write methods use this pool for all server I/O.

## Risks and Edge Cases

Connections are remounted between shares, so concurrent use must be prevented by correct borrow/return discipline. Routine filesystem errors skip echo probing; other errors can evict a valid but transiently failing session. `drainPool` avoids closing while sessions are active, but leaked session counts would keep the pool alive. Kerberos creates a new factory per dial, limiting cache reuse across connections.

## Test Signals

Signals include repeated operations reusing sessions, idle timeout closing unused sessions, failures closing unhealthy connections, active reads preventing drain, Kerberos and NTLM authentication working, and no races under parallel list/read/write workloads.
