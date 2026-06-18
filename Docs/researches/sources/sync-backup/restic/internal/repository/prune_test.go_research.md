
# sources/sync-backup/restic/internal/repository/prune_test.go

Purpose: integration-tests pruning behavior over generated repositories.

`testPrune` creates random blobs, chooses a subset as used, optionally inserts broken/wrong data, builds a `PruneOptions` plan, executes it, reloads indexes, and verifies kept blobs remain while unused packs are removed according to options. `TestPrune` covers multiple option combinations such as MaxUnused, MaxRepack, cacheable-only, unsafe recovery, and uncompressed repacking. `TestPruneSmall` checks small-pack behavior and the threshold that avoids endless repacking for too few small packs.

State and persistence are full repository state: pack files, index files, blob sets, and backend removal. Integration points include `PlanPrune`, `PrunePlan.Execute`, `CopyBlobs`, `RepairIndex`, and repository checker helpers. Risks covered include data-loss prevention, removing stale indexes, unreferenced pack deletion, pack rewrite correctness, and option-specific pruning behavior across repository versions.
