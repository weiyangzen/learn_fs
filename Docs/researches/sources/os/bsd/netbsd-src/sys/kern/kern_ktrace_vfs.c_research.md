# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_ktrace_vfs.c

Read completely: 146 lines.

Implements the VFS-facing `ktrace(2)` syscall wrapper. It opens a pathname as a regular writable vnode-backed file and then delegates trace control to `ktrace_common()` in `kern_ktrace.c`.

Behavior:
- `sys_ktrace()` first enters the ktrace recursion guard with `ktrenter()`.
- For operations other than `KTROP_CLEAR`, it copies in the pathname, opens it with `vn_open()` for read/write, destroys the path buffer, unlocks the vnode, rejects non-regular files with `EACCES`, allocates a temporary file descriptor/file object, and initializes it as a writable vnode file using `vnops`.
- It calls `ktrace_common()` with the operation, facilities, target pid, and optional file pointer.
- For file-requiring operations, it aborts the temporary fd with `fd_abort()` after `ktrace_common()` has consumed or referenced the file as needed.

Integration:
- This file isolates explicit VFS path handling from the trace core, which also supports fd-based tracing through `sys_fktrace()`.
- Uses pathbuf, vnode open/close, file descriptor allocation, and vnode fileops.

Risks and notes:
- The temporary file descriptor consumes a descriptor slot in the tracing process for the duration of the syscall; the source comments state this is expected not to matter.
- On `fd_allocfile()` failure, the code closes the vnode with `FWRITE` even though it was opened with `FREAD|FWRITE`.
