# sources/sync-backup/kopia/snapshot/restore/shallow_fs_output.go

Purpose: local filesystem output wrapper that writes shallow placeholder files instead of full snapshot contents past a configured restore depth or for large files.

Important APIs/types/functions: `ShallowFilesystemOutput`, `makeShallowFilesystemOutput`, overridden `WriteDirEntry`, overridden `WriteFile`, `writeShallowEntry`, and `readonlyfilemode`.

Control flow: only wraps a `*FilesystemOutput`; other outputs are returned unchanged. Directory and large-file entries must implement `snapshot.HasDirEntry`, are serialized via `localfs.WriteShallowPlaceholder`, and then attributed with write bits cleared. Small files below `MinSizeForPlaceholder` are restored normally.

State and persistence: creates placeholder sidecar files on disk and refuses to write one when the real path already exists, avoiding ambiguous future snapshots.

Dependencies and integration points: used by `restore.Entry` when traversal depth exceeds the configured limit. Integrates with localfs shallow placeholder parsing and `SafeRemoveAll`.

Risks and test signals: placeholder writes preserve metadata but not content locally; real-path existence causes a hard error to avoid data loss. Long filename checks happen in the caller for shallow directories and cleanup helpers.
