# File Research: sources/os/bsd/openbsd-src/sys/sys/syslog.h

Syslog priority/facility ABI and logging prototypes.

This header defines `/dev/log`, `LIOCSFD`, maximum log line size, priority constants, facility constants, priority/facility extraction macros, optional `SYSLOG_NAMES` lookup tables, `struct syslog_data`, mask macros, and `openlog()` option flags. Userland prototypes include regular and reentrant syslog APIs plus `sendsyslog()`.

Kernel builds define `LOG_PRINTF` and declare `logpri()`, `log()`, `addlog()`, and `logwakeup()` with kernel printf format checking.

Filesystem/storage relevance: diagnostic. Filesystem, VFS, and storage code use kernel logging paths for warnings and errors, while userland logging reaches `/dev/log`.
