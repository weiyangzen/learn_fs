# sources/sync-backup/kopia/internal/mount/mount_posix_webdav_helper_darwin.go

Purpose: Darwin-specific WebDAV mount helper.

Important APIs/types/functions: `mountWebDavHelper` invokes `mount_webdav`; `unmountWebDavHelper` invokes `umount`.

Control flow: builds an external command with the WebDAV URL and target path, executes it through `exec.CommandContext`, and wraps command errors with output context.

State and persistence behavior: state is held by the OS mount table; the file itself stores none.

Dependencies and integration points: used by `newPosixWedavController` on macOS.

Risks and test signals: external command availability and permissions dominate reliability. Integration tests should cover command failure messages and unmount cleanup on Darwin.
