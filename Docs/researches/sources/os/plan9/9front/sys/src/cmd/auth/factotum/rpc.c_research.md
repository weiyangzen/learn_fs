# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/rpc.c

Factotum `/mnt/factotum/rpc` dispatcher and `/ctl` command parser.

Key responsibilities:
- Enforces paired write/read RPC cycles.
- Parses RPC verbs: `start`, `read`, `write`, `authinfo`, and `attr`.
- Starts protocol modules from `proto=...` attributes and manages implicit close on repeated start.
- Routes protocol read/write calls and formats responses: `ok`, `done`, `needkey`, `toosmall`, `phase`, `error`.
- Serializes `AuthInfo` and injects uid-change capability strings through `mkcap`.
- Logs protocol transitions when debug mode is enabled.
- Parses control verbs: `key`, `delkey`, and `debug`.
- Adds keys for all supplied `proto=` values, splitting public and private attributes.
- Deletes matching keys, allowing private-field patterns only as private queries.

Dependencies:
- Uses factotum `Fsstate`, `Proto`, keyring utilities, confirm/needkey queues, authinfo serialization, and attribute parser/formatter.

Notable risks:
- RPC writes can contain binary arguments after the first verb separator.
- Multi-line control writes are rejected except for a single trailing newline.
