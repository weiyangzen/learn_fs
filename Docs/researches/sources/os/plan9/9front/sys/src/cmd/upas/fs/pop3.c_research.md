# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/pop3.c

This file implements the POP3/APOP backend for `upas/fs`.

Key behavior:
- Supports paths such as `/pop/`, `/pops/`, `/poptls/`, `/popnotls/`, `/apop/`, `/apops/`, `/apoptls/`, `/apopnotls/`.
- Dials POP3/POP3S, negotiates CAPA/STLS where applicable, detects PIPELINING and `EXPIRE 0`, and logs in via APOP or USER/PASS through factotum.
- Uses UIDL to match existing messages, detect deleted/disappeared messages, and create new placeholder messages.
- Downloads new messages with `LIST` and `RETR`, handles dot-stuffing, server size lies, and optional pipelining.
- Deletes marked remote messages using `DELE`.
- Provides mailbox controls for debug/nodebug and refresh interval.

Integration and risks:
- Persists UIDL in `idxaux`.
- `pop3hangup` sends QUIT even if prior protocol state is degraded.
- Message deletion on server is tied to local deleted+inmbox state during sync.
