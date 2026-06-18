# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/extra/tokens.c

This file implements an IMAP-style tokenizer helper for mailbox token parsing tests.

Key behavior:
- `qtoken` handles single-quoted sections, doubled single quotes, and separators.
- `getmtokens` splits on whitespace, either collapsing multiple separators or treating one separator at a time depending on `multiflag`.

Integration and risks:
- Similar in spirit to tokenizer code in IMAP paths; likely used for testing parser edge cases.
