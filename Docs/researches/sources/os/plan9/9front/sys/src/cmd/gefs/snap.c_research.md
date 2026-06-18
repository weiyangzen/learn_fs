# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/snap.c

Snapshot, deadlist, and block-reclamation logic for gefs.

Key responsibilities:
- Caches, loads, creates, flushes, merges, and frees deadlists.
- Records killed blocks into deadlists based on snapshot generations.
- Opens, closes, labels, forks, updates, and deletes snapshot trees.
- Maintains predecessor/successor links and snapshot label/reference counts.
- Reclaims blocks when snapshots are deleted or merged.

Important behavior:
- Mutable snapshots get a new tree generation and `memgen`; immutable labels increment label counts.
- `updatesnap()` creates a new generation for dirty mounted snapshots, relinks history, and can delete the old tree if it becomes unreferenced.
- `killblk()` avoids double-freeing blocks allocated before a fork by comparing block generation with tree base.
- `dlsync()` flushes all cached deadlists into the snapshot tree before sync.

Notable risks:
- Correctness depends on subtle `gen`, `memgen`, `base`, `pred`, and `succ` relationships.
- Deadlist cache eviction flushes metadata and can allocate/write while snapshot metadata is being mutated.
