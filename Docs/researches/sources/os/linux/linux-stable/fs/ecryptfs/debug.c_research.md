# File Research: sources/os/linux/linux-stable/fs/ecryptfs/debug.c

## Summary
Provides debug-only helpers for printing eCryptfs authentication-token details and raw hex dumps under the module verbosity setting.

## Main Responsibilities
- Dump authentication token type, salt, signature, persistence flag, and session-key state.
- Print decrypted or encrypted session-key bytes only when `ecryptfs_verbosity > 0`.
- Provide `ecryptfs_dump_hex()` as the common hex-dump helper used by crypto and keystore code.

## Key APIs
- `ecryptfs_dump_auth_tok()`
- `ecryptfs_dump_hex()`

## Important Behavior
The functions can expose secret key material to the kernel log when verbosity is enabled. `main.c` warns at module init when `ecryptfs_verbosity > 0` because these debug paths can print sensitive values.

## Research Notes
This file has no state of its own. It is purely diagnostic, but security-sensitive because it can log decrypted keys.
