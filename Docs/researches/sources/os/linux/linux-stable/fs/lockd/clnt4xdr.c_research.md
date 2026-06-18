# File Research: sources/os/linux/linux-stable/fs/lockd/clnt4xdr.c

Client-side XDR encoder/decoder for NLM version 4 RPC calls.

Protocol details:
- Uses NFSv3 file handle size and NLMv4 64-bit byte ranges.
- Verifies client owner string size against XDR and NLM maximums at compile time.
- Encodes/decodes cookies, netobjs, caller names, NLM locks, holders, and status results.
- `lockd_set_file_lock_range4()` converts decoded `(offset,length)` into kernel `(start,end)` semantics, including EOF locks.

RPC procedures:
- Defines encode/decode routines for TEST, LOCK, CANCEL, UNLOCK, GRANTED, message variants, and result callbacks.
- `nlm4_procedures[]` maps `NLMPROC_*` IDs to XDR handlers and word-size estimates.
- Exports `nlm_version4` for the common `nlm_program`.

Correctness notes:
- Status values are kept in network byte order for upper layers.
- Invalid status enum values decode as `-EIO`.
- Zero-length cookies from HPUX are normalized to a 4-byte zero cookie.
