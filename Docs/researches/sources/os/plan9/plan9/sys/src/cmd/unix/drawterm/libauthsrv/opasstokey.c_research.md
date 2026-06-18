# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/opasstokey.c

This file implements the older password-to-DES-key derivation.

Key behavior:
- `opasstokey` folds password bytes into a DES key buffer using the original Plan 9 algorithm.

Important details:
- Kept for compatibility with older auth material.
