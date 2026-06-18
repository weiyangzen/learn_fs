# sources/test-tools/syzkaller/pkg/osutil/fileutil.go

Purpose: Provides filesystem helpers for atomic file copying/renaming, test directory population, temporary file writing, and simple content grep across source trees.

Important APIs: `CopyFile`, `Rename`, `FillDirectory`, `WriteTempFile`, and `GrepFiles`.

Control flow: `CopyFile` opens the source, preserves mode and modification time, writes to `<new>.tmp`, closes, sets times, and renames into place. `Rename` tries `os.Rename`, then falls back to copy/remove for cross-device moves. `FillDirectory` creates parent directories and writes files from a map, mainly for tests. `WriteTempFile` creates a temp file with a `syzkaller` prefix and cleans up on write failure. `GrepFiles` walks a root tree, filters by extension, reads files into memory, and returns relative paths containing a target byte sequence.

State and persistence: Mutates the filesystem. Copy operations are near-atomic for the destination but not fsync-backed. `Rename` removes the old file even if fallback copy succeeds but remove fails is ignored.

Dependencies and integration: Used by patch focus-area header scanning, tests, crash memory dump copy paths, and general repository utilities.

Risks: `GrepFiles` skips all files whose extension does not exactly equal `ext`; empty `ext` still filters out files with non-empty extensions due to current condition. It loads entire files into memory. `CopyFile` defers close and also closes explicitly, which is usually harmless.

Test signals: `fileutil_test.go` covers `GrepFiles`; `osutil_test.go` indirectly covers copy/link pattern behavior.
