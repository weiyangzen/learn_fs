# File Research: sources/windows/winfsp/src/dll/library.c

This file contains DLL entry and COM-style self-registration hooks.

Key responsibilities:
- Stores `DllInstance` on process attach.
- On process detach, finalizes FUSE, service, filesystem, event log, POSIX, and well-known SID subsystems, passing whether detach is dynamic.
- On thread detach, finalizes per-thread FUSE state.
- Provides `_DllMainCRTStartup` as a minimal CRT startup alias to `DllMain`.
- `DllRegisterServer` registers the WinFsp fsctl device, network provider, and event log, treating fsctl registration as critical and later registrations as non-critical.
- `DllUnregisterServer` unregisters the same components.

Filesystem relevance:
- This is lifecycle and installation glue for the WinFsp DLL.
- Correct finalization matters because FUSE context storage is thread-local and cleaned during thread detach.
