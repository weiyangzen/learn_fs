<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/path_nix.go -->
# sources/sync-backup/git-lfs/commands/path_nix.go

Purpose: non-Windows platform implementation of path root cleanup and OS line-ending helpers.

Important APIs/types/functions: `cleanRootPath` and `osLineEnding`.

Control flow: `cleanRootPath` returns its input unchanged; `osLineEnding` returns LF.

State and persistence behavior: stateless and read-only.

Dependencies/integration points: selected by build tags `!windows`; used by track path normalization and shared line-ending logic.

Risks and test signals: risks are minimal; behavior assumes Unix-like shells do not rewrite root-style paths like Git Bash on Windows. Test signals are non-Windows builds preserving patterns and defaulting to LF when `core.autocrlf` is not true.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/path_nix.go -->
