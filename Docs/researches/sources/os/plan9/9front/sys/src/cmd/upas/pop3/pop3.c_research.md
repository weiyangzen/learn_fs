# File Research: sources/os/plan9/9front/sys/src/cmd/upas/pop3/pop3.c

Implements a POP3 daemon backed by upas/fs.

Key responsibilities:
- Handles POP3 commands: `CAPA`, `USER`, `PASS`, `APOP`, `STLS`, `STAT`, `LIST`, `UIDL`, `RETR`, `TOP`, `DELE`, `RSET`, `NOOP`, `SYNC`, `QUIT`.
- Performs APOP challenge/response authentication and optional cleartext password login only after TLS or `-p`.
- Starts `/bin/upas/fs -np -f <box>` after login and reads `/mail/fs/mbox`.
- Builds an in-memory message table with upas message numbers, digest, octet counts, and deletion marks.
- Converts line endings to CRLF and dot-stuffs output.
- Deletes marked messages on `SYNC`/`QUIT` via `/mail/fs/ctl`.
- Supports TLS server mode with a configured certificate.

Important functions:
- `readmbox()` starts upas/fs, scans message dirs, reads `digest`, counts header/body lines, and computes POP octet sizes.
- `getcrnl()` reads protocol lines.
- `retrcmd()` and `topcmd()` stream raw messages with POP dot-stuffing.
- `stlscmd()` upgrades fd 0/1 with `tlsServer()`.
- `hello()`, `setuser()`, `dologin()`, `passcmd()`, `apopcmd()` implement authentication.
- `enableaddr()` writes a trusted peer address marker under `/mail/ratify/trusted`.

Filesystem relevance:
- Uses `/mail/fs/mbox` as POP mailbox view.
- Message deletion is a batched `delete mbox <ids>` command to `/mail/fs/ctl`.
- Mailbox path is `/mail/box/<user>/mbox`.

Notable risks and quirks:
- Anti-bruteforce behavior exits or delays on malformed/bad auth and logs likely guessers after repeated failures.
- `CAPA` advertises `STLS` unconditionally even if no cert is configured, though `STLS` then returns an error.
- `readmbox()` unmounts `/mail/fs` before starting its own instance.
