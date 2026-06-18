## sources/sync-backup/syncthing/lib/osutil/atomic.go

Purpose: atomic-ish file writer that writes to a secure temporary file in the destination directory and renames it into place on close.

Important APIs: `ErrClosed`, `TempPrefix`, `AtomicWriter`, `CreateAtomic`, `CreateAtomicFilesystem`, `Write`, and `Close`.

Control flow and state: `CreateAtomic` wraps a basic filesystem rooted at the destination directory; `CreateAtomicFilesystem` creates a secure temp file with `TempFile`. `Write` accumulates the first write error and closes the temp file on failure. `Close` removes the temp file on exit, syncs the temp file best-effort, closes it, records existing destination mode, renames temp to final path, handles Windows read-only rename by chmod/retry, restores previous mode if possible, fsyncs the containing directory best-effort, and marks the writer closed by setting `ErrClosed`.

Persistence behavior: successful close replaces or creates the target path. Existing file mode is preserved after replacement when supported. The temp file is in the same directory for same-filesystem rename semantics, and directory fsync improves crash durability where supported.

Dependencies and integration points: uses Syncthing `fs.Filesystem`, `TempFile`, `build.IsWindows`, and path handling. Used anywhere Syncthing needs durable config/state writes.

Risks: not safe for multiple close/write calls after close beyond returning stored error. Rename atomicity depends on filesystem semantics. Chmod restoration can fail on filesystems without chmod support and is tolerated only if resulting mode matches. The deferred temp removal ignores errors.

Test signals: `atomic_test.go` and `atomic_unix_test.go` cover create, replace, read-only replacement, and temp permissions.
