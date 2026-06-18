# sources/sync-backup/kopia/internal/ospath/ospath_windows.go

Purpose: Windows-specific path initialization and long-filename conversion.

Important APIs/types/functions: Windows `init` and `SafeLongFilename`.

Control flow: initialization chooses Windows config/log directories. `SafeLongFilename` converts long local drive or UNC paths to extended-length forms while leaving short, relative, or already-prefixed paths alone.

State and persistence behavior: only package globals are initialized; no filesystem writes.

Dependencies and integration points: protects Windows filesystem operations that may exceed traditional MAX_PATH limits.

Risks and test signals: extended path prefix handling is subtle for drive letters, UNC shares, and already-safe paths. Windows tests cover these conversions.
