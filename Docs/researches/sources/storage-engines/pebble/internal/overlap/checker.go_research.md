<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/overlap/checker.go -->
# sources/storage-engines/pebble/internal/overlap/checker.go

Purpose: determines whether a user-key region overlaps table boundaries or actual point/range data in an LSM level or whole version, with a best-effort probe path for external ingestion and splitting decisions.

Important APIs/types: `WithLSM`, `WithLevel`, `Kind` (`None`, `OnlyBoundary`, `Data`), `Checker`, `IteratorFactory`, `MakeChecker`, `LSMOverlap`, `LevelOverlap`, `EmptyRegion`, and internal empty-region helpers.

Control flow and state: `LSMOverlap` checks L0 sublevels first and stops on data overlap; then checks levels 1+. `LevelOverlap` performs a cheap boundary test: no file means `None`, file boundaries inside the region mean pessimistic `Data`, and a single enclosing file may be probed unless `SkipProbe` says not to. `EmptyRegion` checks point keys/range deletions and then range keys by opening iterators only when metadata bounds overlap. Fragment iterators are probed with `First` or `SeekGE` based on known lower bounds.

Persistence and integration: no persistent state; uses manifest metadata and table iterators supplied by callers. Integrates with `manifest.Version`, `LevelSlice`, `base.UserKeyBounds`, `keyspan`, and external ingestion code that can skip remote probes. Risks include false positives by design, iterator errors propagating, assumptions about metadata bounds, empty span assertions, and opening files for probes. Datadriven tests cover boundary/data/range cases and iterator-open behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/overlap/checker.go -->
