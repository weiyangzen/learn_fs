# File Research: sources/os/linux/linux/fs/lockd/clnt4xdr.c

Purpose: Client-side XDR encoder/decoder for NLM version 4 RPC calls.

Key functionality:
- Defines XDR word-size estimates for NLMv4 request/reply types.
- Clamps Linux `loff_t` ranges to NLMv4 signed 64-bit wire limits.
- Encodes cookies, caller names, file handles, owner handles, locks, lockargs, cancelargs, unlockargs, and result/test replies.
- Decodes cookies, NLMv4 statuses, and denied-lock holder data.
- Maps holder offsets into `struct file_lock` using `lockd_set_file_lock_range4()`.
- Exposes `nlm_version4` RPC version table with all standard NLM procedures.

Dependencies and integration:
- Used by the NLM client RPC program table in `clntxdr.c` when `CONFIG_LOCKD_V4` is enabled.
- Depends on `struct nlm_args`, `struct nlm_res`, and status constants from `lockd.h`/`nlm.h`.

Risk notes:
- Wire status values are intentionally kept in network byte order for upper layers.
- Cookie decode accepts empty HPUX cookies by substituting a zero 4-byte cookie.
- Invalid status enum values or oversized cookies return `-EIO`.
