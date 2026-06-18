# sources/sync-backup/kopia/snapshot/restore/tar_output.go

Purpose: `restore.Output` implementation that serializes restored entries into a tar stream.

Important APIs/types/functions: `TarOutput`, `Parallelizable`, `BeginDirectory`, `Close`, `WriteFile`, `CreateSymlink`, and `NewTarOutput`.

Control flow: tar output is not parallelizable, so restore uses one worker. Non-root directories emit directory headers. Files open their snapshot reader, write a `tar.Header`, then stream bytes with `io.Copy`. Symlinks read their target and emit `tar.TypeSymlink` headers. Incremental existence checks always return false.

State and persistence: writes tar records to the supplied `io.WriteCloser`; no local filesystem entries are inspected or modified.

Dependencies and integration points: consumed by `restore.Entry` as an archive target and relies on `archive/tar` plus Kopia `fs` metadata.

Risks and test signals: directory finish and shallow dir-entry hooks are no-ops; extended attributes are not represented here. Caller must close to flush tar footer and wrapped writer. Restore statistics provide indirect signals.
