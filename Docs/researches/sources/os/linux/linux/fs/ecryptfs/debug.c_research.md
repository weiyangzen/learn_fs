# File Research: sources/os/linux/linux/fs/ecryptfs/debug.c

## Purpose
Provides debugging-only helpers for printing authentication-token state and hex dumps.

## Main Responsibilities
- `ecryptfs_dump_auth_tok()` prints the shape and selected fields of an `ecryptfs_auth_tok`.
- `ecryptfs_dump_hex()` prints binary data using `print_hex_dump()` when verbosity permits.

## Behavior
`ecryptfs_dump_auth_tok()` distinguishes private-key and passphrase tokens, prints salt and signature for passphrase tokens, and reports session-key flags such as userspace decrypt/encrypt requests, decrypted key presence, and encrypted key presence. If `ecryptfs_verbosity > 0`, it dumps decrypted or encrypted key bytes.

`ecryptfs_dump_hex()` is a guard around `print_hex_dump()` and returns immediately unless verbosity is at least 1.

## Dependencies
- Shared declarations and constants from `ecryptfs_kernel.h`.
- `ecryptfs_printk()` filtering from `main.c`.

## Risks and Notes
- These helpers can expose sensitive key material to kernel logs when verbosity is enabled.
- The module initialization path warns that nonzero verbosity writes secret values to syslog.
