# sources/sync-backup/git-lfs/tools/robustio.go

Purpose: non-Windows wrappers for rename/open/remove.

Important APIs/types/functions: `RobustRename`, `RobustOpen`, and `RobustRemove`.

Control flow: direct delegation to `os.Rename`, `os.Open`, and `os.Remove`.

State and persistence: performs the requested filesystem operation; no retries or extra state on non-Windows.

Dependencies and integration points: called by file replacement and transfer resume cleanup paths; Windows file supplies retry behavior.

Risks: inherits platform `os` semantics with no retry on transient errors.

Test signals: indirectly exercised by file/transfer tests.
