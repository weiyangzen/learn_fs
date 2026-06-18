# sources/sync-backup/git-lfs/tools/robustio_windows.go

Purpose: Windows retrying wrappers for filesystem operations affected by sharing/access races.

Important APIs/types/functions: `isEphemeralError`, `isFileInUseError`, `robustRemoveRetryDelaysMs`, `RobustRename`, `RobustOpen`, and `RobustRemove`.

Control flow: uses `retry.Do`; rename/open retry sharing violations, remove retries sharing violation and access denied with Git-like millisecond delay pattern.

State and persistence: performs actual filesystem operations; local `result` stores opened file across retry closure.

Dependencies and integration points: used by file replacement and download resume code to tolerate Windows file locking. Depends on `github.com/avast/retry-go` and `x/sys/windows`.

Risks: retry windows are short; persistent antivirus/indexer locks still fail. `RobustOpen` assigns `result` even when an error occurs, so callers rely on final returned error.

Test signals: no direct Windows robustio test in this subset.
