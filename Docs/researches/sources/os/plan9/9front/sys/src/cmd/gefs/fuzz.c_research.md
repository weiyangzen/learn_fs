# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/fuzz.c

Concurrent gefs B-tree fuzzer and shadow-model verifier.

Key responsibilities:
- Generates random directory-entry, data-pointer, insert, delete, clobber, and wstat messages.
- Maintains an AVL shadow map of expected key/value state.
- Runs writer and scanner/checker workers against a mutable `fuzz` snapshot.
- Verifies random lookups and complete scans against the shadow tree.
- Dumps trace data to `/tmp/fuzz.trace` and kills the process group on mismatch.

Important behavior:
- Uses xoshiro-like local PRNG state seeded from `fuzzseed`.
- `fzupsert()` snapshots tree root state, performs `btupsert()`, then applies the same batch to the shadow model.
- `fzscan()` periodically performs both sampled lookups and full in-order scans.
- `fzinit()` creates a mutable `fuzz` snapshot from `empty` and seeds shadow state from existing entries.

Notable risks:
- Shadow selection in `pickrand()` walks the AVL shape heuristically rather than by exact rank.
- The fuzzer intentionally runs forever once enabled.
