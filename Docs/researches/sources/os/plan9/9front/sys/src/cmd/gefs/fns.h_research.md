# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/fns.h

Shared gefs extern declarations, packing macros, prototypes, and debug/error macros.

Key contents:
- Declares global filesystem state and runtime flags.
- Provides big-endian `PACK*`/`UNPACK*` macros for gefs disk structures.
- Declares block allocation/cache/sync, snapshot, load/ream, B-tree, user, dump, pack/unpack, channel, worker, and fuzz APIs.
- Defines tracing, assertion, fatal, and Plan 9-style error-stack macros.

Role:
- Connects gefs compilation units without exposing implementation-specific headers.
- Establishes the internal API surface for block, tree, snapshot, 9P, admin, and test code.

Notable constraints:
- `waserror()`/`poperror()` depend on per-process `Errctx` setup in `main.c`.
- Many APIs assume callers already hold `fs->mutlk` or are inside an epoch.
