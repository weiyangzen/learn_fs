# sources/sync-backup/git-lfs/subprocess/path_windows.go

Purpose: Windows implementation of executable lookup with `PATHEXT` support.

Important functions: `chkStat`, `hasExt`, `findExecutable`, and `findPathExtensions`.

Control flow: `findPathExtensions` normalizes `PATHEXT` entries to lowercase dotted extensions or defaults to `.com`, `.exe`, `.bat`, `.cmd`. `findExecutable` checks the exact path if extensions are disabled or the filename already has an extension, then tries each extension. `chkStat` rejects directories.

State/persistence behavior: reads `PATHEXT` and filesystem metadata only.

Dependencies/integration: compiled only on Windows for `subprocess.LookPath`.

Risks: lowercasing `PATHEXT` assumes case-insensitive filesystem behavior. `hasExt` must distinguish drive/path separators from file extensions.

Test signals: Windows CI command spawning and test tool discovery validate this behavior.
