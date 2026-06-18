## sources/sync-backup/syncthing/lib/fs/basicfs_lstat_windows.go

Purpose: Windows `Lstat` implementation with optional directory junction treatment as directories.

Important APIs/types/functions: `readReparseTag`, `isDirectoryJunction`, `dirJunctFileInfo`, `junctionPointModeMask`, and `BasicFilesystem.underlyingLstat`.

Control flow: `readReparseTag` opens the path with backup semantics and open-reparse-point flags, then queries `FILE_ATTRIBUTE_TAG_INFO`. Init builds a mode mask for junction points based on Go runtime version. `underlyingLstat` calls `os.Lstat`; if junction-as-dirs is enabled and the mode indicates a junction-like reparse point, it reads the tag and wraps mount points as `dirJunctFileInfo`, whose mode and `IsDir` simulate a traversable directory.

State and persistence: Read-only metadata and runtime-version-derived mask.

Dependencies and integration points: Windows build tag; used by `BasicFilesystem.Lstat`, directory walking, and option `OptionJunctionsAsDirs`.

Risks: Windows reparse semantics changed around Go 1.23, so version checks are fragile. Opening reparse points can fail on some filesystems; errors fall back to ordinary `Lstat` result.

Test signals: Windows-specific basic filesystem tests outside this subset should cover junction behavior.
