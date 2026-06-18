# File Research: sources/teaching/minix/minix/servers/vfs/misc.c

Miscellaneous VFS system calls, PM-side lifecycle hooks, VM callbacks, reboot handling, coredump entry, DS events, and diagnostics.

Key syscall handlers:
- `do_getsysinfo`: superuser-only export of fproc/dmap/fproc_light/call-stats data.
- `do_fcntl`: implements descriptor flags, status flags, advisory locks, `F_FREESP`, `O_NOSIGPIPE`, and cache flush control.
- `do_sync`: syncs all mounted filesystems.
- `do_fsync`: syncs all mounts on the same device as a descriptor.
- `do_vm_call`: handles VM-to-VFS fd lookup, fd close, and fd I/O/peek requests.
- `do_svrctl`: VFS parameter get/set and diagnostics.
- `do_getrusage`: obsolete stub returning OK.

VM integration:
- `dupvm` duplicates a process FD into VM if the file’s filesystem supports `RES_HASPEEK` and the vnode is regular or block-special.
- `do_vm_call` supports:
  - `VMVFSREQ_FDLOOKUP`
  - `VMVFSREQ_FDCLOSE`
  - `VMVFSREQ_FDIO`
- VM replies use `VM_VFS_REPLY` asynchronously.

PM/lifecycle functions:
- `pm_reboot`: syncs, frees processes, unmounts filesystems, forces unmounts, and replies to PM.
- `pm_fork`: copies parent `fproc`, preserves child mutex, increments filp and vnode references.
- `pm_exit`: frees process state.
- `pm_setgid`, `pm_setgroups`, `pm_setuid`, `pm_setsid`: update VFS-side credentials/session/TTY state.
- `pm_dumpcore`: creates `core.<pid>`, writes ELF core data, then exits the process through `free_proc`.

`free_proc` behavior:
- Unpauses blocked processes.
- Closes all open descriptors.
- Releases root and working directories.
- On real exit, unsuspends endpoint waiters, unmaps dmap/smap/vmnt associations, stops waiting workers, handles controlling TTY revocation, and marks the process slot free.

Other behavior:
- `ds_event` consumes DS driver-up events and calls `dmap_endpt_up` or `smap_endpt_up`.
- `panic_hook` prints VFS thread stack traces.

Notable implementation details:
- `F_FLUSH_FS_CACHE` is superuser-only and flushes either the block special’s backing FS cache or the hosting FS device.
- `pm_reboot` deliberately fakes worker process context while freeing other process slots.
- `pm_dumpcore` cannot dump a running process without termination because it unblocks and changes the target process state.
