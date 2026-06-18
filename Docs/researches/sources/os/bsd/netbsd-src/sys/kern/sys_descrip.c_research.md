# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_descrip.c

Read completely: 746 lines.

This file implements system calls on file descriptors: duplication, `fcntl`, close, stat/pathconf, advisory locking, fadvise, and pipe creation.

Major functions:
- `sys_dup`, `dodup`, `sys___dup3100`, and `sys_dup2` duplicate descriptors through `fd_dup`/`fd_dup2`, checking limits and managing file references.
- `fcntl_forfs` handles filesystem-specific `F_FSCTL` commands, including bounded copyin/copyout buffers.
- `do_fcntl_lock` implements POSIX record lock commands using `fo_advlock`.
- `sys_fcntl` handles `F_CLOSEM`, `F_MAXFD`, lock commands, descriptor duplication with close-on-exec/fork variants, FD flags, `FNOSIGPIPE`, file status flags, owner get/set, path lookup, and seals.
- `sys_close` validates then closes a descriptor and maps `ERESTART` to `EINTR`.
- `do_sys_fstat` and `sys___fstat50` call fileops stat and copy results out.
- `sys_fpathconf` calls `fo_fpathconf` if supported.
- `sys_flock` maps BSD flock semantics to advisory lock operations over the whole file.
- `do_posix_fadvise` and `sys___posix_fadvise50` route file advice to fileops.
- `sys_pipe` and `sys_pipe2` create pipes through `pipe1`.

Integration: this is a syscall-facing wrapper over the file descriptor table and `fileops`. It coordinates with vnode path reconstruction, socket/vnode/file controls, kauth indirectly through lower layers, and UVM readahead via included fadvise support.

Reliability notes: `F_SETFL` updates nonblocking and async state through ioctls and attempts rollback on failure, but the comment notes it is not guaranteed atomic. `F_CLOSEM` loops from `fd_lastfile` down and tolerates concurrent descriptor table changes. FS-specific fcntl data size is capped by `F_PARAM_MAX` and stack vs heap buffers are selected by `STK_PARAMS`.
