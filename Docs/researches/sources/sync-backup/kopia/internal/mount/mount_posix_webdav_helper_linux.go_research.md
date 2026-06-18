# sources/sync-backup/kopia/internal/mount/mount_posix_webdav_helper_linux.go

Purpose: Linux-specific WebDAV mount helper.

Important APIs/types/functions: `mountWebDavHelper` uses `mount -t davfs`; `unmountWebDavHelper` uses `umount`.

Control flow: delegates mounting and unmounting to system commands under the caller context and returns wrapped command errors.

State and persistence behavior: mount table state is managed by the operating system; no process-local state is stored here.

Dependencies and integration points: depends on davfs support and is called by the POSIX WebDAV controller.

Risks and test signals: Linux hosts may lack `davfs2` or require privileges; command output should be surfaced for diagnostics. Tests are mostly integration or command-wrapper substitution tests.
