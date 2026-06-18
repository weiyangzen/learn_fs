## sources/sync-backup/syncthing/lib/osutil/atomic_test.go

Purpose: tests creation and replacement behavior of `AtomicWriter`.

Important tests: `TestCreateAtomicCreate` verifies target file does not appear before close and contains written data after close. `TestCreateAtomicReplace` and `TestCreateAtomicReplaceReadOnly` share `testCreateAtomicReplace` to replace existing writable and read-only files while preserving old permissions.

Control flow and state: tests create temp directories/files, write through `CreateAtomic`, close, read final data, and stat permissions.

Dependencies and integration points: uses real OS filesystem paths, not fake filesystem, so it exercises platform rename/chmod behavior.

Risks: permission checks can vary by OS; read-only mode handling is especially platform-sensitive.

Test signals: strong regression coverage for atomic create/replace and mode preservation.
