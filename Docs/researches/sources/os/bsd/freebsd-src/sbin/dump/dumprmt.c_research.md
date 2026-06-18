# File Research: sources/os/bsd/freebsd-src/sbin/dump/dumprmt.c

Implements the client side of the historical remote tape protocol used by `dump` when RDUMP support is enabled and an output target uses `host:tape` syntax.

Key responsibilities:
- Establishes a remote shell connection to the remote `rmt` program using `rcmd()`.
- Parses optional `user@host` remote endpoint syntax and validates usernames with `okname()`.
- Wraps remote tape operations: `rmtopen`, `rmtclose`, `rmtread`, `rmtwrite`, split write phases, `rmtseek`, `rmtstatus`, and `rmtioctl`.
- Tracks remote tape state with `TS_CLOSED` / `TS_OPEN`.
- Reads protocol replies of the form `A...`, `E...`, and `F...`, mapping remote errors into local `errno`.

Important data:
- `rmtpeer`: mutable remote host string, possibly split at `@`.
- `rmtape`: socket fd to the remote `rmt` command.
- `errfd`: stderr side channel from `rcmd()`.
- `mts`: global `struct mtget` populated by bytewise reads from `rmtstatus()`.

Notable behavior:
- `rmtgetconn()` uses service `shell/tcp`, local passwd name, `RMT` environment override, and fallback `_PATH_RMT`.
- Socket buffers are sized from `ntrec * TP_BSIZE`, capped around 60 KiB plus protocol slack.
- TCP options prefer throughput and disable Nagle via `TCP_NODELAY`.
- `SIGPIPE` is treated as remote connection loss and exits with `X_ABORT`.

Risks and constraints:
- Relies on legacy `rcmd()` / remote shell semantics.
- `rmtpeer` is modified in place when parsing `user@host`.
- `rmtseek()` uses `int offset`, with a comment noting the `off_t` mismatch.
- Protocol desynchronization is fatal via `rmtconnaborted()`.
