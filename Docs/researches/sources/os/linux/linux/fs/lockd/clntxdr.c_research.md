# File Research: sources/os/linux/linux/fs/lockd/clntxdr.c

Purpose: Client-side XDR encoder/decoder for NLM versions 1 and 3, plus the root `nlm_program` RPC program table.

Key functionality:
- Defines XDR size estimates for NLMv1/v3 procedures.
- Clamps lock offsets to 32-bit NLM wire limits.
- Encodes/decodes cookies, fixed NFSv2 file handles, lock owners, lock ranges, statuses, test replies, and generic result replies.
- Creates RPC procedure tables for NLMv1 and NLMv3.
- Builds `nlm_versions[]`, optionally including `nlm_version4` from `clnt4xdr.c`.
- Exports `nlm_program`.

Dependencies and integration:
- Used by `host.c` when creating RPC clients for lockd peers.
- Shares upper-layer `nlm_args`/`nlm_res` structures with `clntproc.c`.

Risk notes:
- NLMv2 is intentionally not implemented.
- Wire status values remain network byte order.
- 32-bit range conversion treats zero length or overflow as lock-to-EOF.
