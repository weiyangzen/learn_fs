# sources/sync-backup/kopia/snapshot/restore/local_fs_output_unix.go

Purpose: Linux, FreeBSD, and OpenBSD symlink attribute helpers for local filesystem restore.

Important APIs/types/functions: `symlinkChown`, `symlinkChmod`, and `symlinkChtimes`.

Control flow: owner changes use `unix.Lchown`; chmod is a no-op because Linux does not support symlink permissions in the way restore needs; timestamp updates use `unix.Lutimes`.

State and persistence: changes symlink owner and timestamps where the OS permits, without following the link target. Mode restoration is intentionally skipped.

Dependencies and integration points: called by `FilesystemOutput.setAttributes` for symlink entries under the Unix build tag.

Risks and test signals: no-op chmod means restored symlink permission bits may not match metadata on platforms with different semantics. Errors are surfaced to the common caller unless permission ignoring is enabled.
