# sources/sync-backup/git-lfs/tools/util_generic.go

Purpose: fallback clone-file implementation for platforms other than Linux, Darwin, and Windows.

Important APIs/types/functions: `CheckCloneFileSupported`, `CloneFile`, and `CloneFileByPath`.

Control flow: reports unsupported platform for probing; clone attempts return `(false, nil)`.

State and persistence: none.

Dependencies and integration points: preserves cross-platform API for `CopyWithCallback`.

Risks: callers must correctly fall back to byte copy when clone returns false.

Test signals: `util_test.go` checks these methods exist on all platforms.
