# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/fs/pop3.c

## Purpose
POP3 mailbox backend for `upas/fs`, fetching remote mail into the mail filesystem view and deleting remote messages when local messages are marked deleted.

## Main Interfaces
- `pop3mbox`: parses `/pop`, `/apop`, TLS, SSL, and no-TLS mailbox paths.
- `pop3sync`: dial/login/read/purge/hangup cycle.
- `pop3login`, `pop3capa`, `pop3pushtls`: authentication and security negotiation.
- `pop3read`: UIDL-based mailbox reconciliation.
- `pop3download`: retrieves and parses one message.
- `pop3purge`: issues `DELE` for deleted messages.
- `pop3ctl`: mailbox control commands for debug, thumbprint, refresh.

## Behavior
The backend prefers APOP when available unless plain POP is requested, negotiates STLS or SSL variants, records UIDLs to match existing messages, downloads only new messages, parses them through `mbox.c`, and schedules refresh via `waketime`. It supports POP3 pipelining by forking a writer process that batches `LIST/RETR` or `DELE`.

## Dependencies
Uses Plan 9 auth/factotum (`auth_respond`, `auth_getuserpasswd`), TLS (`tlsClient`, thumbprints), `Biobuf`, `dial`, SHA1, and mailfs parser/message APIs.

## Risks / Notes
- Certificate thumbprint checking is compiled out with `if(0)`, so TLS currently verifies only that a certificate exists.
- POP3 size claims are treated as unreliable; buffers grow during `RETR`.
- UIDL longer than RFC limits is ignored.
