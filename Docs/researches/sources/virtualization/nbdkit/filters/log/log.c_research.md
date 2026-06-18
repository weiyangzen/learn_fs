# File Research: sources/virtualization/nbdkit/filters/log/log.c

Implements the logging filter’s nbdkit callbacks. Configuration accepts `logfile=`, `logappend=`, and `logscript=`.

`log_get_ready()` opens the logfile with `O_CLOEXEC`, records the original PID, and emits a Ready message. `log_after_fork()` logs Fork only in forked children. `log_list_exports()` and `log_preconnect()` log global operations with static IDs.

Per-connection `log_open()` assigns a connection number, stores interned export name and TLS state, and `log_prepare()` logs export, TLS, size, block sizes, and negotiated capability values. `log_finalize()` logs Disconnect with transaction count.

Request callbacks wrap `pread`, `pwrite`, `flush`, `trim`, `zero`, `extents`, and `cache`, logging offsets, counts, flags, extent lists, return values, and protocol-level error names.
