# sources/sync-backup/kopia/snapshot/restore/local_fs_output_darwin.go

Purpose: Darwin-specific symlink attribute helpers for local filesystem restore.

Important APIs/types/functions: `symlinkChown`, `symlinkChmod`, and `symlinkChtimes`.

Control flow: owner changes use `unix.Lchown`, mode changes use `unix.Fchmodat` with `AT_SYMLINK_NOFOLLOW`, and timestamp updates use `unix.Lutimes` with nanosecond conversion.

State and persistence: modifies metadata on the symlink itself rather than its target, preserving restore semantics for archived symlink entries.

Dependencies and integration points: selected by Go build constraints for Darwin and called by `FilesystemOutput.setAttributes` when the remote entry implements `fs.Symlink`.

Risks and test signals: platform support for symlink modes varies, and permission errors may be filtered by `IgnorePermissionErrors` in the caller. Coverage is mostly integration-level through restore behavior on macOS.
