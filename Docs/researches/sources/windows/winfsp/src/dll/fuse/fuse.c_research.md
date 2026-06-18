# File Research: sources/windows/winfsp/src/dll/fuse/fuse.c

Core WinFsp FUSE compatibility layer setup, option parsing, mount-channel handling, notifications, TLS context, and errno mapping.

Key responsibilities:
- Defines `struct fuse_chan` carrying a Windows mount point.
- Defines supported FUSE/WinFsp core mount options and parser actions.
- Lazily allocates a TLS key for `struct fuse_context`.
- Implements `fsp_fuse_mount` and `fsp_fuse_unmount`.
- Converts SDDL, token users, user/group names, and UID maps into Windows security/SID/UID state.
- Parses core options such as debug logging, umasks, uid/gid, reparse/link behavior, volume name, UNC/volume prefix, filesystem name, file security, cache timeouts, thread count, and POSIX unlink/rename support.
- Creates and initializes a `struct fuse` with WinFsp volume parameters in `fsp_fuse_new`.
- Preflights the WinFsp disk or network device and mount point.
- Implements destroy, exit, exited, notify, context allocation, and errno-to-NTSTATUS mapping.

Important behavior:
- Mount-point parsing accepts `*`, drive letters, `\\?\X:`, `\\.\X:`, absolute Windows paths, and optionally environment-converted paths.
- Debug mode redirects WinFsp debug logging to stderr or a configured append file.
- If uid/gid is `-1`, it queries the process token; Azure AD users get a default uidmap compatible with the comment’s Cygwin expectation.
- FUSE defaults set case-sensitive search, case-preserved names, persistent ACLs, reparse-point support, device control support, and `UmFileContextIsUserContext2`.
- `fsp_fuse_notify` maps POSIX-ish notification actions to Windows `FILE_NOTIFY_CHANGE_*` filters and `FILE_ACTION_*` actions, uppercasing names for case-insensitive filesystems.
- Per-thread FUSE contexts are allocated on demand and released by `fsp_fuse_finalize_thread`.

Dependencies:
- Includes `dll/fuse/library.h` and `sddl.h`.
- Uses WinFsp core APIs (`FspFileSystemPreflight`, `FspFileSystemNotify`, `FspDebugLogSetHandle`), POSIX mapping helpers, Windows token/SID/security APIs, FUSE option parsing helpers, and `errno.i`.

Notable risks:
- Option parsing mixes FUSE conventions with Windows-specific options, so compatibility behavior depends on exact string matching.
- TLS context cleanup is incomplete for dynamic DLL unload, as noted by the file comment.
- UID/SID mapping is limited to eight explicit uidmap entries.
