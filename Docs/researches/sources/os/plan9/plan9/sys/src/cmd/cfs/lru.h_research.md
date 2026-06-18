# File Research: sources/os/plan9/plan9/sys/src/cmd/cfs/lru.h

This header defines the LRU list node and operations used by `cfs`.

Key contents:
- `Lru` struct with previous and next pointers.
- Prototypes for list initialization, append, mark-recent, and mark-unrecent operations.

Filesystem relevance:
- Direct support for `cfs` cache replacement policy.
