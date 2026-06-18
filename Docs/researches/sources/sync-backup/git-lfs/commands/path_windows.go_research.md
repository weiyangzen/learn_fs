<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/path_windows.go -->
# sources/sync-backup/git-lfs/commands/path_windows.go

Purpose: Windows implementation of path root cleanup and OS line endings, specifically compensating for Git Bash drive-prefix expansion.

Important APIs/types/functions: globals `winBashPrefix`, `winBashMu`, `winBashRe`; functions `osLineEnding`, `cleanRootPath`, and `winPathHasDrive`.

Control flow: `osLineEnding` returns CRLF. `cleanRootPath` locks, returns non-drive paths unchanged, lazily locates Git Bash root by inspecting the `pwd` executable path and deriving a forward-slash prefix, then replaces that prefix with `/`. `winPathHasDrive` lazily compiles a drive-letter regex.

State and persistence behavior: process-local cached Git Bash prefix and regex; no filesystem writes.

Dependencies/integration points: used by track path normalization for Windows/Git Bash input, depends on `subprocess.ExecCommand("pwd")` and filepath path derivation.

Risks and test signals: risks include deriving the wrong prefix from unusual `pwd` locations, replacing only first prefix occurrence, concurrency around regex initialization mostly protected by caller lock for `cleanRootPath` but not direct `winPathHasDrive`, and mixed slash cases. Test signals include `C:/Program Files/Git/foo` conversion, normal relative paths unchanged, backslash drive paths, missing `pwd`, and concurrent calls.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/path_windows.go -->
