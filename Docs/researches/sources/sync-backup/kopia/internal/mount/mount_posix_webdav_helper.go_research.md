# sources/sync-backup/kopia/internal/mount/mount_posix_webdav_helper.go

Purpose: provides the POSIX WebDAV mount controller used when FUSE is unavailable or explicitly bypassed.

Important APIs/types/functions: `posixWedavController`, `newPosixWedavController`, `Unmount`, `MountPath`, and `Done`.

Control flow: starts a Kopia WebDAV server with `DirectoryWebDAV`, mounts its URL at the target path with platform helper commands, and returns a controller that first unmounts the OS mount then stops the WebDAV server. Temporary mount directories are removed during unmount.

State and persistence behavior: tracks mount point, wrapped WebDAV controller, done channel from the WebDAV server, and temp-dir ownership.

Dependencies and integration points: calls build-tagged `mountWebDavHelper` and `unmountWebDavHelper`, plus `DirectoryWebDAV`.

Risks and test signals: failure after WebDAV start but before OS mount must clean up the server; helper command behavior differs by OS. Tests should inject helper failures, verify temp-dir cleanup, and ensure `Done` reflects server shutdown.
