# sources/sync-backup/git-lfs/subprocess/path_nix.go

Purpose: Unix implementation of executable detection for `LookPath`.

Important APIs/functions: `findPathExtensions` returns nil; `findExecutable` checks `os.Stat`, not-directory, and any execute bit.

Control flow: direct stat of candidate path. A regular executable path is returned; missing/stat errors propagate; non-executable or directory returns `os.ErrPermission`.

State/persistence behavior: read-only filesystem metadata inspection.

Dependencies/integration: compiled on non-Windows platforms and used by `subprocess.ExecCommand`.

Risks: execute permission check uses any execute bit (`0111`) rather than effective user access evaluation. Symlink handling is delegated to `os.Stat`.

Test signals: command execution failures on Unix would surface if lookup incorrectly rejects executable tools.
