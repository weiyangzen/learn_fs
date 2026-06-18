# sources/test-tools/syzkaller/pkg/manager/diff_store.go

Purpose: Provides an in-memory plus filesystem artifact store for patch-diff fuzzing results. It tracks per-title base and patched crash counts, verification status, repro files, repro logs, reports, and crash logs.

Important APIs and types: `DiffBugStatus` defines `pending`, `verifying`, `completed`, and `ignored`. `DiffBug` has `PatchedOnly` and `AffectsBoth` classifiers. `DiffBugInfo` records counts, a base-not-crashed proof, and relative artifact paths. `DiffFuzzerStore` exposes `UpdateStatus`, `BaseCrashed`, `EverCrashedBase`, `BaseNotCrashed`, `PatchedCrashed`, `SaveRepro`, `List`, and `PlainTextDump`.

Control flow and state: All mutations go through `patch`, which initializes the `bugs` map and locks `mu`. `BaseCrashed` marks completed and increments base count; `BaseNotCrashed` records proof only if no base crash exists. `PatchedCrashed` increments patched count and saves first crash log. `SaveRepro` stores crash logs using Unix timestamp names, switches to repro title when the repro title differs, and stores syzkaller repro plus stats log.

Persistence: Files are saved under `BasePath/crashes/<crashHash(title)>/<name>`, while stored paths are relative (`crashes/...`). File writes use `osutil.MkdirAll` and `osutil.WriteFile`; errors are ignored by `saveFile`, which is a risk.

Dependencies and integration: Consumed by diff manager and HTTP dashboard diff tables. Reuses `crashHash` and `reproFileName` from manager crash storage.

Risks: Store is not durable across manager restart because the bug map is not reloaded from disk. Timestamp filenames can collide if multiple saves for the same title occur within one second. Ignoring write errors can make UI paths point at missing files.

Test signals: Indirectly covered by diff manager tests for status transitions; no dedicated persistence tests in this shard.
