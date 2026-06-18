# sources/storage-engines/pebble/merger.go

Purpose: this public API file re-exports Pebble merge operator types from `internal/base` and provides a small helper to finish merge operations that may request deletion of the merged value.

Important APIs/types/functions: `Merge`, `Merger`, `ValueMerger`, and `DeletableValueMerger` are type aliases. `DefaultMerger` exposes the base default. `finishValueMerger` accepts a `ValueMerger` and `includesBase` flag, then calls `DeletableFinish` when the merger implements `DeletableValueMerger`, otherwise falls back to `Finish`.

Control flow: `finishValueMerger` is a two-branch adapter. In the deletable case it returns value, `needDelete`, closer, and error from `DeletableFinish`; in the regular case it returns value, closer, and error from `Finish`, leaving `needDelete` false.

State and persistence behavior: this file stores no mutable state beyond the exported default alias. Merge state is owned by concrete `ValueMerger` implementations provided by options or tests. Any returned closer must be handled by callers.

Dependencies and integration points: merge operators are used by read paths, compaction, and validation code such as `CheckLevels` to combine merge operands with base values. The type aliases keep the public package API stable while implementation types live under `internal/base`.

Risks and test signals: the main risk is caller mishandling of `needDelete` or `closer`, not this adapter itself. Compatibility risk is high for alias changes. Test coverage is indirect through merge behavior tests and checker tests that use failing mergers.
