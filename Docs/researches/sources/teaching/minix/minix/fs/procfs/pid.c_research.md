# File Research: sources/teaching/minix/minix/fs/procfs/pid.c

`pid.c` defines the files generated inside each dynamic PID directory: `psinfo`, `cmdline`, `environ`, and `map`. Each entry maps a filename to a generator function taking a kernel process slot.

`get_proc_data` retrieves detailed process data through `__sysctl(CTL_MINIX, MINIX_PROC, PROC_DATA, pid)`. `is_zombie` checks `proc_list` flags for process slots.

`pid_psinfo` emits the compact process information format used by `mtop(1)`: version, process type, endpoint, sanitized name, state, blocked-on endpoint, priority, user/system time, cycle counters, VM memory total, nice value, and effective UID. It combines data from MINIX process sysctl, `proc_list`, and optional VM usage information.

`pid_cmdline` and `pid_environ` fetch argv/environment data through kernel sysctl nodes, skip kernel tasks and zombies, and append raw NUL-separated records to the ProcFS buffer. `pid_map` queries VM regions by endpoint and emits address ranges with read/write/execute protection flags.
