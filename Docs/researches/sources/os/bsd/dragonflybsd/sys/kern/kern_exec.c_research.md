# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_exec.c

## Role

Implements process image replacement for `execve()` and `fexecve()`: argument/environment copyin, executable vnode lookup/open/permission checks, image activator dispatch, first-page mapping, vmspace replacement, user stack construction, descriptor and signal cleanup, setuid/setgid credential handling, text vnode/namecache tracking, and exec image activator registration.

## Major Entry Points

- `sys_execve()` checks `SYSCAP_NOEXEC`, initializes a name lookup for the user path, copies arguments, calls `kern_execve()`, frees args, and aborts the process on lethal post-vmspace errors.
- `sys_fexecve()` obtains a vnode-backed file from a descriptor, requires read-only/readable access, supplies a `/dev/fd/N` path for interpreted scripts, and calls `kern_execve()` with the file.
- `kern_execve()` is the central exec path. It resolves the executable vnode, checks permissions, maps the first page, dispatches image activators, handles interpreter recursion, creates the new stack, unshares fd/signal tables as needed, resets process state, applies credentials, updates process text vnode/namecache, posts exec notifications, and sets registers.
- `exec_new_vmspace()` is called by image activators at the point of no return. It kills other LWPs, sets `P_INEXEC`, stalls external process holders, replaces or clears the vmspace, removes user mappings, resets TID state, and creates the new stack mapping.

## Argument and Stack Handling

- `exec_copyin_args()` uses an object cache sized for `PATH_MAX + ARG_MAX`, stores argv strings followed by env strings, stores the filename separately at `buf + ARG_MAX`, handles `argv == NULL` as `EFAULT`, and supplies the filename as argv[0] if the argv array is empty.
- `exec_copyout_strings()` builds the initial user stack: argv vector, env vector, ELF auxargs space, argument/environment strings, randomized stack gap, spare space, execpath for rtld, signal trampoline code, and `ps_strings`.
- `stackgap_random` is sysctl-controlled and must be zero, negative fixed gap, or a positive power of two no larger than 16 pages.
- Process argument caching stores argv bytes in `p_args` if the cache size is within `ps_arg_cache_limit`.

## Executable File and VM Handling

- `exec_check_permissions()` requires no `MNT_NOEXEC` on the executable mount or top-level mount, at least one execute bit, regular file type, nonzero size, successful `VOP_EACCESS(VEXEC)`, no active writers (`v_writecount`), and successful `VOP_OPEN(FREAD)`.
- `exec_map_page()` maps executable file pages through the vnode's VM object, first trying shared object/page lookup and falling back to `vm_page_grab()` plus `vm_pager_get_page()`.
- `exec_map_first_page()` maps page zero for image activators; `exec_unmap_page()` and `exec_unmap_first_page()` release lwbuf and page holds.
- `exec_new_vmspace()` either executes from a resident vmspace copy, clears a private vmspace, or creates a new vmspace when the old one is shared.

## Process State Changes

- Other LWPs are killed for multithreaded exec via `killalllwps(1)`.
- Shared file descriptor tables are copied so descriptors cannot remain shared after exec.
- Shared signal action tables are copied so `execsigs()` can reset handlers privately.
- Per-LWP and per-process user mappings are removed; virtual kernel state is not inherited.
- Profiling stops, `FD_CLOEXEC` descriptors close, caught signals reset, process/thread command names update, `P_EXEC` is set, vfork parent wait state is cleared, `AFORK` is cleared, and registers are initialized.

## Credentials and Security

- Setuid/setgid is honored only when mount flags allow it and the process is not traced.
- Set-id exec disables tracing unless `ktrace_suid` allows it for privileged callers, clears parent-death signal, applies descriptor safety checks for fds 0..2, updates effective uid/gid, and clears local varsym state.
- Saved uid/gid are updated to POSIX values after exec.
- `caps_exec(p)` adjusts credentials/capabilities for the new image.

## VFS/File-System Relevance

- Exec is fundamentally vnode-backed here: namecache lookup (`nlookup`), `cache_vget()`, vnode attributes, `VOP_EACCESS`, `VOP_OPEN`, vnode pager page-in, `vn_fullpath()`, `vn_mark_atime()`, and persistent `p_textvp`/`p_textnch` are all managed in this file.
- `fexecve()` depends on descriptor-to-vnode resolution and honors close-on-exec behavior for interpreted scripts.
- Mount flags (`MNT_NOEXEC`, `MNT_NOSUID`) directly affect execution.

## Research Notes

- The `vmspace_destroyed` flag has two meanings: any point-of-no-return state and ownership of clearing `P_INEXEC`.
- Error handling after `exec_new_vmspace()` can return `-1`, causing the caller to terminate the process.
- Interpreter recursion preserves/rewrites lookup state and must clean up first-page and vnode references before retrying.
- This file is essential for research into executable file access, text vnode lifetime, VM object reads through VFS, and process lifecycle interactions with file descriptors.
