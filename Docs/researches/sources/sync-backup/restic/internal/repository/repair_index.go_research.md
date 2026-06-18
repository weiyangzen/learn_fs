
# sources/sync-backup/restic/internal/repository/repair_index.go

Purpose: rebuilds or repairs repository index files by comparing index references with actual pack files and optionally reading all packs from scratch.

Important APIs are `RepairIndex`, `RepairIndexOptions`, and `rewriteIndexFiles`. In `ReadAllPacks` mode, existing index IDs are remembered as obsolete and the in-memory index is cleared. Otherwise, indexes are loaded with a callback that marks invalid indexes obsolete, then pack sizes are computed from index contents. The repair scans backend pack files, identifies missing/unindexed/size-mismatched packs, reindexes packs that need reading via `createIndexFromPacks`, and removes references to packs absent from the backend.

State changes include new index files, deletion of obsolete/old indexes via `MasterIndex.Rewrite`, and clearing the in-memory index after completion. Integration points include pack header parsing, repository index load/flush, prune's index rewrite path, and progress reporting. Risks include losing valid index entries, retaining missing-pack references, handling damaged indexes without aborting, and ensuring invalid pack files are skipped rather than indexed. Tests in `repair_index_test.go` cover valid, damaged, missing index, and missing pack cases in both modes.
