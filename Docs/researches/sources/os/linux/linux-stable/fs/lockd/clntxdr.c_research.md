# File Research: sources/os/linux/linux-stable/fs/lockd/clntxdr.c

Client-side XDR encoder/decoder for NLM versions 1 and 3.

Protocol details:
- NLMv2 is intentionally not implemented.
- Uses NFSv2 fixed file handle size and 32-bit lock offsets/lengths.
- `loff_t_to_s32()` clamps kernel offsets to NLMv1/v3 range.
- `nlm_compute_offsets()` emits length zero for lock-to-EOF.

XDR coverage:
- Encodes/decodes booleans, int32, netobj, cookies, file handles, status, holders, caller names, and lock structs.
- Handles TEST, LOCK, CANCEL, UNLOCK, GRANTED, async message variants, and result callbacks.
- Normalizes empty HPUX cookies to a 4-byte zero cookie.
- Rejects oversized cookies and invalid status enum values.

RPC program integration:
- `nlm_procedures[]` maps `NLMPROC_*` procedures to handlers and sizing constants.
- Defines version 1 and version 3 `rpc_version` tables.
- `nlm_program` includes versions 1, 3, and optionally 4.
