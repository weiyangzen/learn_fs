# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/strlog.h

`strlog.h` defines the STREAMS log driver control interface. Its main data structure, `log_ctl_t`, is the control portion of a log message and carries module ID, sub-ID, trace level, disposition flags, boot/epoch time fields, sequence number, and syslog-style priority. The time field layout is explicitly adjusted for LP64 compatibility using 32-bit clock/time types.

Public log flags (`SL_FATAL`, `SL_NOTIFY`, `SL_ERROR`, `SL_TRACE`, `SL_CONSOLE`, `SL_WARN`, `SL_NOTE`) specify where and how log messages are delivered. Private implementation flags add console-only, log-only, user-terminal, and panic-message routing.

`trace_ids_t` identifies module/sub-ID/level filters used by `I_TRCLOG`. Log-driver I_STR ioctl command numbers are based under `LOGCTL` and define tracer, error logger, and console logger roles (`I_TRCLOG`, `I_ERRLOG`, `I_CONSLOG`).

`STRLOG_MAKE_MSGID()` hashes a printable format string into a six-digit message ID range. Kernel builds declare `strlog()` and `vstrlog()` with printf format checking. The `STRLOG` macro compiles to `strlog` in debug/lint builds and to a short-circuited expression otherwise, making debug trace logging disappear in non-debug builds.
