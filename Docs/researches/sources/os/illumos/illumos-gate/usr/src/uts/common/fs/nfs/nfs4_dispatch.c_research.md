# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_dispatch.c

Purpose: Dispatches NFSv4 RPC requests and implements the NFSv4.0 duplicate request cache.

Key behavior:
- Initializes/finalizes the duplicate request cache with a global LRU list plus per-XID hash buckets.
- `rfs4_find_dr` keys duplicate entries by RPC XID and remote transport address, returning NEW, REPLAY, PENDING, or ERROR.
- Reuses free or replayable DRC entries once the configured maximum cache size is reached.
- `rfs40_dispatch` runs NFSv4.0 COMPOUND requests, caches replies for non-idempotent requests, replays cached replies for duplicates, and avoids caching when the thread would block.
- Sends minor-version mismatch replies when a COMPOUND requests a disabled minor version.
- `rfs4_dispatch` handles NULL procedure, minor-version routing, NFSv4.0 dispatch, and NFSv4.1+ handoff to `rfs4x_dispatch`.

Dependencies:
- Uses RPC/SVC/XDR infrastructure, NFSv4 compound execution/free helpers, NFSv4 idempotency detection, server global state, DTrace probes, and list primitives.

Notable details:
- DRC entries transition through NEW/INUSE/REPLAY/FREE states under the DRC mutex.
- Pending duplicates are dropped without reply so the client retransmits.
- Resource exhaustion replies synthesize a one-op COMPOUND result with `NFS4ERR_RESOURCE` or `NFS4ERR_OP_ILLEGAL`.
