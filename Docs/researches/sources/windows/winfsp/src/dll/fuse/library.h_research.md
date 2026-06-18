# File Research: sources/windows/winfsp/src/dll/fuse/library.h

This is the internal header for the WinFsp FUSE 2 layer.

Key contents:
- Includes DLL internals plus FUSE public headers.
- Defines `FSP_FUSE_LIBRARY_NAME`, context-header conversion macros, symlink capability macros, Cygwin/MSVC `ENOSYS` mapping, and NFS reparse constants.
- Defines internal `struct fuse`, holding:
  - Environment pointer.
  - Parsed mount/permission options.
  - FUSE operations and private data.
  - Capability flags and initialized state.
  - Volume parameters, label, mountpoint, loop event, WinFsp filesystem pointer.
  - FUSE3 backpointer and base file security descriptor.
- Defines per-thread `fsp_fuse_context_header`, open-file descriptor state, and directory enumeration handle state.
- Provides allocation helpers `fsp_fuse_obj_alloc` / `fsp_fuse_obj_free`.
- Declares TLS context access, core option data, core parser, operation guards, directory filler helpers, token uid/gid helper, and `fsp_fuse_intf`.

Filesystem relevance:
- This header defines the private state shared by all FUSE 2 adapter files.
- The context-header layout is important: per-request POSIX path storage is placed immediately before `struct fuse_context`.
