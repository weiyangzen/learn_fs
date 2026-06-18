# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_sysctl.c

Read completely: 3010 lines.

Implements OpenBSD's legacy numeric `sysctl(2)` dispatch and many kernel/hardware sysctl handlers. The file is the central router from user MIBs into `CTL_KERN`, `CTL_HW`, `CTL_NET`, `CTL_VM`, `CTL_VFS`, `CTL_MACHDEP`, optional debug/DDB trees, and numerous kernel information export helpers.

Core dispatch and locking:
- `sys_sysctl()` validates privilege for writes, copies in the MIB, applies `pledge_sysctl()`, selects the top-level handler, copies in/out `oldlenp`, and uses `sysctl_vslock()` for handlers that need the old buffer wired while the kernel lock is held.
- `sysctl_vslock()` and `sysctl_vsunlock()` serialize large user-buffer locking with `sysctl_lock`, check against `uvmexp.wiredmax`, call `uvm_vslock()`/`uvm_vsunlock()`, and bracket the operation with `KERNEL_LOCK()`.
- `kern_sysctl_dirs()` dispatches non-terminal `KERN_*` nodes, with some handlers avoiding the generic buffer wiring path and others going through `kern_sysctl_dirs_locked()`.
- `kern_sysctl()` handles terminal kernel variables, message buffers, mbuf stats, CPU time, pool debug, bounded integer variables, and falls back to `kern_sysctl_locked()` for entries requiring the global sysctl locking path.

Kernel and hardware variables:
- Stores mutable kernel attributes such as `hostname`, `domainname`, `hostid`, cached `disknames`, `diskstats`, and `securelevel`.
- `kern_vars[]` and `hw_vars[]` define bounded/read-only integer sysctls used by `sysctl_bounded_arr()`.
- `kern_sysctl_locked()` handles securelevel, hostname/domainname updates, name-cache/fork stats, stack-gap tuning, buffer cache percentage, PF status, console device, and UTC offset.
- `hw_sysctl()` reports machine/model, online CPU count, physical/user memory, firmware strings, UUID, sensors, disk information, CPU speed/performance policy, powerdown control, ucom names, CPU topology controls, and battery charge controls.

Sysctl helper API:
- Integer helpers include `sysctl_int_lower()`, `sysctl_int()`, `sysctl_rdint()`, `sysctl_securelevel()`, `sysctl_securelevel_int()`, `sysctl_int_bounded()`, `sysctl_bounded_arr()`, and `sysctl_rdquad()`.
- String helpers include writable `sysctl_string()`, truncating `sysctl_tstring()`, internal `sysctl__string()`, and read-only `sysctl_rdstring()`.
- Structure helpers include writable `sysctl_struct()` and read-only `sysctl_rdstruct()`.
- Write helpers commonly copy in before changing state, but several preserve historical behavior where a new value may be committed before a later copyout error is reported.

Process and file introspection:
- `fill_file()` builds `struct kinfo_file` records for vnodes, sockets, pipes, kqueues, process-owned file descriptors, cwd/root/text/trace vnodes, and network PCB/socket state. Kernel pointers are exposed only to privileged callers.
- `sysctl_file()` implements `KERN_FILE_BYFILE`, `KERN_FILE_BYPID`, and `KERN_FILE_BYUID`, walking file tables, process lists, vnode references, and inet PCB tables; it estimates needed output size and returns `ENOMEM` if the provided buffer is too small.
- `sysctl_doproc()` enumerates live and zombie processes for `KERN_PROC_*` queries, optionally including threads, using `fill_kproc()` for each result.
- `fill_kproc()` fills `struct kinfo_proc` from process/thread state, credentials, sessions, tty state, VM RSS, usage aggregates, start time converted through boot time, CPU id, `%cpu`, and synthesized process state.
- `sysctl_proc_args()` reads argv/env vectors from another process's user VM via `uvm_io()`, with system/exiting/execing checks and owner/root checks for environment access.
- `sysctl_proc_cwd()` returns another process's current working directory through `vfs_getcwd_common()`.
- `sysctl_proc_nobroadcastkill()` exposes and optionally changes `PS_NOBROADCASTKILL` for a process.
- `sysctl_proc_vmmap()` exposes chunks of a process or kernel address map as `struct kinfo_vmentry`, requiring root for non-self and kernel-map queries.

Device, disk, IPC, and sensor exports:
- `sysctl_diskinit()` maintains cached disk name and diskstats arrays under `sysctl_disklock`, rebuilding on disk topology changes and refreshing statistics on request.
- `sysctl_sysvipc()` exports SysV IPC info for msg/sem/shm depending on kernel options, with partial-buffer handling.
- `sysctl_sensors()` copies out sanitized sensor device or individual sensor records.
- `sysctl_cpustats()` and `sysctl_cptime2()` export per-CPU times through `sysctl_ci_cp_time()`, which uses per-CPU generation-protected counters.
- `sysctl_audio()` and `sysctl_video()` expose optional recording/control toggles.
- `sysctl_utc_offset()` stores timezone offset in minutes through `KERN_UTC_OFFSET`, then adjusts the realtime clock and writes the RTC.

Security and concurrency notes:
- Writes require `suser()` at syscall entry; individual handlers add securelevel, owner/root, or subsystem-specific restrictions.
- `securelevel` prevents lowering by non-init processes under restrictive conditions and makes some sysctls read-only above securelevel 0.
- Kernel pointer exposure in process/file sysctls is gated by privilege.
- The file mixes global kernel locking, rwlocks, mutexes, vnode/process references, PCB locks, and per-CPU counter generation loops; callers must respect the old numeric sysctl ABI and its buffer-size semantics.
