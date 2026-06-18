# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/pop3/pop3.c

## Purpose
POP3 server exposing a local upas mailbox through the POP3 protocol.

## Main Interfaces
- POP commands: `USER`, `PASS`, `APOP`, `CAPA`, `STLS`, `STAT`, `LIST`, `UIDL`, `RETR`, `TOP`, `DELE`, `RSET`, `SYNC`, `QUIT`.
- `readmbox`: starts `upas/fs -np -f <box>`, reads `/mail/fs/mbox`, and builds POP message metadata.
- `dologin`: validates APOP/factotum response, changes user identity, creates namespace, and opens mailbox.

## Behavior
The daemon advertises APOP challenge on greeting, optionally allows cleartext password only with `-p` or after TLS, supports STLS with configured certificate, computes POP byte sizes by adding CR bytes to mailfs raw lengths, dot-stuffs output, and deletes marked messages by writing `delete mbox ...` to mailfs control on sync/quit.

## Dependencies
Plan 9 auth (`auth_challenge`, `auth_response`, `auth_chuid`), TLS server, `/bin/upas/fs`, `/mail/fs`, `Biobuf`, `libsec`.

## Risks / Notes
- Cleartext password is disabled unless explicitly allowed or TLS is active.
- Auth failures exponentially back off and eventually terminate.
- `enableaddr` writes a trust marker under `/mail/ratify/trusted`.
