# File Research: sources/windows/winfsp/src/dll/fuse/fuse_intf.c

This is the central WinFsp-to-FUSE adapter. It implements `FSP_FILE_SYSTEM_INTERFACE fsp_fuse_intf`, translating WinFsp filesystem requests into FUSE 2 callbacks and converting results back into NTSTATUS, Win32 file information, security descriptors, reparse buffers, directory buffers, and extended attributes.

Key responsibilities:
- Operation guard hooks: `fsp_fuse_op_enter` / `fsp_fuse_op_leave` establish per-request `fuse_context`, map Windows paths to POSIX paths, derive uid/gid/pid from access tokens, and apply coarse/fine SRW locking around namespace-sensitive operations.
- File metadata: `fsp_fuse_intf_GetFileInfoFunnel` converts `getattr`/`fgetattr` data into `FSP_FSCTL_FILE_INFO`, including directory/reparse classification, allocation rounding, timestamps, inode index, dot-hidden handling, and optional `stat_ex` flags.
- Security translation: POSIX uid/gid/mode are merged into Windows security descriptors; set-security maps modified descriptors back into chmod/chown operations.
- Create/open/lifecycle: implements create, open, overwrite, cleanup, close, read, write, flush, file info, basic info, and file-size paths using the relevant FUSE callbacks.
- Directory enumeration: builds WinFsp directory buffers via `readdir`/legacy `getdir`; supports readdir-plus metadata fast path and post-fixes entries with `getattr` when needed.
- Delete/rename: checks delete access, verifies directory emptiness through enumeration, and maps Windows rename semantics including collision checks.
- Reparse points: maps POSIX symlinks and special files to Windows symlink/NFS reparse points; setting reparse points creates hidden temporary FUSE nodes and renames them over the placeholder.
- EAs/xattrs: maps Windows extended attributes to FUSE xattr operations.
- Device control: maps WinFsp control codes into Linux-compatible FUSE ioctl command values.
- Token utility: `fsp_fuse_get_token_uidgid` maps Windows token user/owner/primary group SIDs to POSIX uid/gid.

Important dependencies:
- Internal types and macros from `dll/fuse/library.h`.
- WinFsp APIs for path conversion, operation context, directory buffers, reparse resolution, security descriptor conversion, and filesystem dispatch.
- FUSE callback table `struct fuse_operations`.

Filesystem relevance:
- This file is the behavioral core for exposing a FUSE filesystem through the Windows filesystem stack.
- It documents many semantic impedance mismatches: Windows delete-on-close vs FUSE unlink, Windows symlink directory/file distinction, Windows ACLs vs POSIX permissions, EAs vs xattrs, and reparse-point creation over an already-created placeholder.

Notable watchpoints:
- `SetReparsePoint` is explicitly described as unreliable/error-prone because it must create a hidden object and rename it over the placeholder.
- Some Windows attribute merge behavior in overwrite is intentionally incomplete.
- Cleanup paths in complex security/reparse functions should be audited carefully because several allocations and descriptor lifetimes are conditional.
