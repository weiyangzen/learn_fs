# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/fs/imap4.c

- Role: IMAP/IMAPS mailbox backend for `upas/fs`.
- Key backend hooks: `imap4mbox` recognizes `/imap/host[/user[/mailbox]]` and `/imaps/...`, initializes `Mailbox.sync`, `Mailbox.close`, and `Mailbox.ctl`; `imap4sync` dials/logs in, reads server state, fetches new mail, purges deleted mail, and schedules refresh.
- Protocol flow: `imap4cmd` sends tagged commands; `imap4resp` parses tagged/untagged responses, `EXISTS`, `STATUS`, `FETCH`, literal bodies, quoted bodies, UID lists, and errors.
- Message fetch: `imap4read` obtains UID list, reconciles with local messages, pipelines `UID FETCH ... BODY[]` requests, calls `imap4fetch`, parses messages, computes SHA1 digest, and plumbs new/deleted mail.
- TLS/auth: `imap4dial` uses `imaps` with `tlsClient` when required; password obtained via `auth_getuserpasswd`; thumbprints are initialized but active checking is disabled by `if(0 && ...)`.
- Control: Mailbox ctl supports `debug`, `nodebug`, `thumbprint`, and `refresh [seconds]`.
- Risks/notes: Response parser uppercases entire lines, which is safe for IMAP verbs but can alter quoted/literal metadata parsing if not already separated. TLS certificate thumbprint enforcement is disabled in code.
