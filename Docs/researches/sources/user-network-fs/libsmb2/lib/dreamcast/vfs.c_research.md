# sources/user-network-fs/libsmb2/lib/dreamcast/vfs.c

Purpose: Provides a KallistiOS/Dreamcast VFS handler that mounts an SMB share under `/smb` using libsmb2 synchronous APIs.

Important APIs/functions: Public entry points are `kos_smb_init(const char *url)` and `kos_smb_shutdown(void)`. VFS operations include open/close/read/write/readdir/rename/unlink/stat/mkdir/rmdir/seek64/tell64/readlink/rewinddir/fstat. `smb2_stat_convert` maps `smb2_stat_64` to KOS `struct stat`.

Control flow: Initialization creates an SMB context, parses the URL, connects to the share, logs success, and registers the VFS handler. Each VFS callback takes a global mutex, calls the corresponding libsmb2 operation, logs failures, and returns KOS-compatible values. Shutdown unregisters the handler and disconnects/destroys global SMB resources.

State/persistence: Uses global `cxt`, `smb_url`, and static VFS handler `vh`; all operations serialize on a single static mutex. Each open file/directory gets an allocated `struct smb_fd` wrapping type and handle, with optional embedded `dirent_t` storage for directories.

Dependencies/integration: Depends on KallistiOS headers (`kos.h`, VFS/NMMGR types, mutex macros, `dbglog`) and libsmb2 public synchronous APIs. The handler path is `/smb`.

Risks: `smb_readdir` logs warning on normal end-of-directory because it treats NULL as an error unconditionally. `strncpy` may leave `dirent.name` unterminated when the SMB name length is at least `NAME_MAX - 1`. Initialization failure paths do not always null globals after cleanup. Shutdown assumes init succeeded. The single global connection prevents multiple SMB mounts and serializes all I/O.

Test signals: Dreamcast/KOS integration tests should mount a test share, list directories including EOF, read/write/seek/stat files, handle long names, and call shutdown after failed init paths. Threaded tests should verify mutex serialization.
