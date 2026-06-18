# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/tree.c

Core gefs copy-on-write B-tree implementation.

Key responsibilities:
- Encodes/decodes leaf values and pivot-buffer messages.
- Performs sorted batched upserts using pivot-buffer messages and flush-down compaction.
- Applies insert, delete, clear, clobber, wstat, and snapshot relink operations.
- Splits, rotates, merges, and balances leaf and pivot blocks.
- Frees replaced data pointers and old tree blocks through deferred reclamation.
- Provides lookup and prefix/in-order scan APIs.

Important behavior:
- Pivot blocks have two regions: child pointers and buffered mutation messages.
- `btupsert()` sorts message batches, tries fast pivot-buffer insertion, otherwise finds a victim path and flushes messages toward leaves.
- Tree updates are COW: new blocks are allocated, old blocks are freed after root replacement.
- `btlookup()` walks to a leaf, then applies pending messages from ancestors from bottom to top.
- `btnext()` merges leaf values with pending pivot-buffer inserts/deletes to produce current scan state.
- Root height can grow or shrink during flush.

Notable risks:
- Very dense pointer arithmetic and fixed-size packed records make corruption bugs hard to localize.
- Correctness depends on preserving room for at least one message during pivot operations.
- `btupsert()` asserts `fs->mutlk` is already held.
