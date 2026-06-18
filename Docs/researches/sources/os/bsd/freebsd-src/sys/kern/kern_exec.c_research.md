# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_exec.c

Read status: complete file reviewed.

This file implements process image replacement, exec argument management, executable permission checks, VM replacement, user stack setup, image activator registration, and core dump output helpers. It is the central `execve(2)` path for named files, file-descriptor exec, and MAC-aware exec.

Main entry points include `sys_execve`, `sys_fexecve`, `sys___mac_execve`, `pre_execve`, `post_execve`, `kern_execve`, `exec_cleanup`, `exec_map_first_page`, `exec_unmap_first_page`, `exec_onexec_old`, `exec_new_vmspace`, `exec_map_stack`, `exec_copyin_args`, `exec_alloc_args`, `exec_free_args`, `exec_args_add_fname`, `exec_args_add_arg`, `exec_args_add_env`, `exec_args_adjust_args`, `exec_copyout_strings`, `exec_check_permissions`, `exec_register`, `exec_unregister`, `core_write`, `core_output`, and `sbuf_drain_core_output`.

The main control flow is `sys_*execve` -> `pre_execve` -> argument copyin -> `kern_execve` -> `do_execve` -> image activator dispatch. `pre_execve` single-threads multithreaded processes at an exec boundary, and `post_execve` either upgrades successful exec to `SINGLE_EXIT` so old sibling threads die or releases the single-thread boundary on failure. `exec_cleanup` frees the old vmspace after successful replacement.

`do_execve` sets `P_INEXEC`, resolves the executable by path, interpreter vnode, or fd, audits the vnode, checks permissions, maps the first page, computes setuid/setgid/MAC credential transitions, and iterates registered `execsw` image activators. Interpreted scripts loop back through `interpret`, dropping text refs and vnode state from the script before activating the interpreter. After activation it copies strings and aux data to the new stack, unshares fds and paths, closes close-on-exec descriptors, resets signals, updates process names, installs credentials, updates text vnode/binname fields, emits kqueue `NOTE_EXEC`, notifies DTrace/PMC/HWT hooks, and initializes registers.

Permission checks require a regular non-empty executable file on an executable mount, pass MAC and VOP access checks, set a text reference with `VOP_SET_TEXT`, and open the vnode for read. Security-sensitive handling includes Capsicum path restrictions for interpreter resolution, suppression of setid transitions on `MNT_NOSUID`, tracing, capability mode, or `P2_NO_NEW_PRIVS`, fd safety for setid exec, clearing inherited death signals on credential changes, and resetting syscall tracing for setid programs.

VM setup is split between `exec_new_vmspace` and `exec_map_stack`. The former destroys or replaces the address space, handles shared-page cleanup, drops System V shared memory, clears ASLR/W^X/wirefuture map flags, invokes process-exec handlers, and calls ABI-specific `sv_onexec`. The latter maps the main stack, applies ASLR stack offset, maps the ABI shared page or guard page, and records `vm_stacktop`, `vm_maxsaddr`, and shared page base.

Argument handling uses preallocated exec KVA ranges stored in a global and per-CPU cache. `exec_prealloc_args_kva` initializes ranges, `exec_alloc_args_kva` obtains one, and the low-memory handler advances a generation so freed ranges get `MADV_FREE`. String assembly enforces `ARG_MAX`, preserves filename, argument, and environment order, and supports interpreter prepending through `exec_args_adjust_args`.

Core dump helpers write sparse or compressed memory segments. `core_output` faults user pages in runs, writes present pages, extends holes for absent pages, tolerates EFAULT from truncated mapped files, and can return EINTR if SIGKILL arrives when `kern.core_dump_can_intr` is enabled. `sbuf_drain_core_output` safely drains procstat-like notes even when called with the process lock held.

Sysctls expose `kern.ps_strings`, `kern.usrstack`, `kern.stackprot`, `kern.ps_arg_cache_limit`, `kern.disallow_high_osrel`, `security.bsd.map_at_zero`, core dump packing toggles, and interruptible core dump behavior.

Risk areas are rollback after partial exec, vnode lock/ref/text accounting across interpreter loops, setid credential timing, old vmspace cleanup when exec failure occurs after VM destruction, argument KVA lifetime under low memory, fd table unsharing before close-on-exec, and coredump behavior for changing user mappings.
