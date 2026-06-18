# sources/sync-backup/git-lfs/subprocess/path.go

Purpose: custom executable lookup derived from Go's `exec.LookPath` behavior, with platform-specific extension handling.

Important API: `LookPath(file string)`.

Control flow: if the file contains a path separator, it checks that path directly with `findExecutable`. Otherwise it iterates `PATH`, treats empty Unix path entries as `.`, skips empty Windows entries, joins each dir with the file, and returns the first executable.

State/persistence behavior: reads `PATH`; no writes.

Dependencies/integration: used by `ExecCommand` on all platforms before assigning `cmd.Path`.

Risks: behavior intentionally diverges by platform. On Unix, empty PATH elements execute from current directory; on Windows they do not. It returns `exec.ErrNotFound` rather than preserving detailed permission errors.

Test signals: platform command spawning and Windows extension lookup indirectly validate this path logic.
