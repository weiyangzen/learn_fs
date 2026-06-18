# sources/sync-backup/git-lfs/tools/filetools_windows.go

Purpose: Windows path canonicalization that resolves symlink/final paths through Win32 handles.

Important APIs/types/functions: `openSymlink` and `CanonicalizeSystemPath`.

Control flow: opens the path with `CreateFile` and backup semantics, repeatedly calls `GetFinalPathNameByHandle` growing the UTF-16 buffer until it fits, then strips `\?\` and normalizes UNC output.

State and persistence: opens and closes a Windows file handle; no durable writes.

Dependencies and integration points: depends on `golang.org/x/sys/windows`; supplies the Windows implementation consumed by `ResolveSymlinks` and `CanonicalizePath`.

Risks: handle open flags are readless but still may fail on permissions; buffer sizing must remain correct for long paths; prefix stripping is Windows-specific and easy to regress.

Test signals: no direct file in this subset, but Windows path behavior is exercised by platform tests elsewhere.
