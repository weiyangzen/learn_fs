# sources/sync-backup/git-lfs/git/ls_files.go

Purpose: wraps `git ls-files -z` to collect cached and optionally untracked file paths, indexed by full path and basename.

Important APIs/types/functions: `lsFileInfo`, `LsFiles`, and `NewLsFiles`.

Control flow: builds `git ls-files -z --cached` arguments, adds `--sparse` for Git 2.35+, optional `--exclude-standard` and `--others`, runs in `workingDir`, scans stdout split on NUL, drains stderr concurrently, and waits for command completion.

State/persistence behavior: read-only query of Git index and working tree. Returned maps persist full path and basename grouping in memory.

Dependencies/integration: depends on `gitNoLFS`, `tools.SplitOnNul`, Git version checks, and is used by gitattr file discovery to locate `.gitattributes`.

Risks/test signals: large stderr is drained to prevent deadlock. Errors include stderr text. Behavior depends on Git version and current index state.
