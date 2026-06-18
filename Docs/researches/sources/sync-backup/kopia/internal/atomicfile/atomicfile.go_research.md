## sources/sync-backup/kopia/internal/atomicfile/atomicfile.go

Purpose: thin wrapper for atomic file writes that normalizes long filenames through Kopia path handling.

Important APIs/types/functions: `Write(filename string, r io.Reader) error`.

Control flow, state, and persistence: delegates to `atomic.WriteFile(ospath.SafeLongFilename(filename), r)`. It persists exactly the reader content through the third-party atomic-write implementation.

Dependencies and integration points: used by shallow placeholder writing and other code that needs atomic replacement on Windows-safe paths.

Risks and test signals: risks are inherited from `natefinch/atomic` behavior and path normalization. No direct tests in this subset.
