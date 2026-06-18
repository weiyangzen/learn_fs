# File Research: sources/local-fs/xfsprogs/db/sig.h

Header for `xfs_db` SIGINT helpers.

Key responsibilities:
- Declares `blockint`, `clearint`, `init_sig`, `seenint`, and `unblockint`.

Dependencies:
- Used by command loops or long-running operations needing interrupt polling.

Notable risks:
- Exposes only global interrupt state, with no per-operation context.
