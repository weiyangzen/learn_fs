# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/crypt.c

This file implements block DES encryption/decryption wrappers for Plan 9 auth data.

Key behavior:
- `encrypt` applies DES encryption over 7-byte chunks expanded into 8-byte DES blocks.
- `decrypt` reverses the operation.

Important details:
- Uses `setupDESstate`, `block_cipher`, and auth key layout expected by Plan 9 ticket code.
- Returns `0` on success and `-1` for invalid lengths.
