# File Research: sources/os/bsd/openbsd-src/sys/sys/resourcevar.h

Defines kernel-private resource-limit sharing and resource/accounting helpers.

Key contents:
- `struct plimit`: copy-on-write, refcounted array of `struct rlimit`.
- `ADDUPROF` macro for deferred profiling updates from AST.
- `profclock_period` extern.
- Inline `lim_read_leave()` and `lim_cur()`.

Key APIs:
- Profiling/accounting: `addupc_intr`, `addupc_task`, `profclock`, `tuagg_*`, `calctsru`, `calcru`.
- Limit lifecycle: `lim_startup`, `lim_free`, `lim_fork`, `lim_read_enter`, `lim_cur_proc`.
- Resource usage: `ruadd`, `rucheck`.

Risk notes:
- `plimit` is shared copy-on-write after fork; updates must respect the rlimit locking protocol.
