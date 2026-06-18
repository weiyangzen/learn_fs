# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/fsenc.c

This file maps IMAP mailbox names to filesystem-safe names and back.

Key behavior:
- Encodes tab as `#0`, space as `##`, and literal `#` as `#1`.
- Maps IMAP `INBOX` to filesystem `mbox`.
- `decfs` reverses escaping and maps filesystem `mbox` back to IMAP `INBOX`.
- Contains a disabled test `main` under comment.

Integration and risks:
- Used by folder/mailbox naming helpers.
- Only escapes a small ASCII set; other filesystem-invalid cases are handled by higher-level `okmbox`/cleaning logic.
