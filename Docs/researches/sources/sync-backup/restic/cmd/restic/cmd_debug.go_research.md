# sources/sync-backup/restic/cmd/restic/cmd_debug.go

Purpose: debug-build-only command registration and implementations for repository introspection and pack examination.

Important APIs/types/functions: build tag `debug` enables `registerDebugCommand`, `newDebugCommand`, `newDebugDumpCommand`, and `newDebugExamineCommand`. `DebugExamineOptions` controls extraction, reupload, and repair attempts. `runDebugDump` dumps indexes, snapshots, packs, or combined data. `runDebugExamine` resolves pack IDs and calls `repository.ExaminePack`.

Control flow/state: dump opens a read lock and writes JSON/index/pack metadata. examine opens an append lock, loads indexes, then examines each requested pack. Options can extract blobs to the current directory or reupload repaired blobs, making examine potentially mutating.

Dependencies/integration: compiled only with `-tags debug`; uses repository dump/examine internals, data snapshot iteration, restic ID lookup, and UI progress.

Risks/test signals: debug commands expose internals and repair/extract flags can write local files or repository blobs. The file has no direct tests in this subset and is excluded from normal builds unless debug tags are enabled.
