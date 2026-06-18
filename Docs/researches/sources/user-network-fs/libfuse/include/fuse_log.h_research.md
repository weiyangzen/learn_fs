# sources/user-network-fs/libfuse/include/fuse_log.h

`fuse_log.h` defines libfuse's process-global logging API. It lets library code and filesystem applications emit syslog-level messages and replace the default stderr logger with a custom handler or syslog.

`enum fuse_log_level` mirrors syslog severities from emergency through debug. `fuse_log_func_t` is a thread-safe callback receiving a level, printf-style format, and `va_list`. Public functions are `fuse_set_log_func`, `fuse_log`, `fuse_log_enable_syslog`, and `fuse_log_close_syslog`; `fuse_log` carries a printf-format compiler attribute.

Runtime flow is global dispatch: libfuse calls `fuse_log`, and the current handler receives the message. Applications can install a handler before session creation because parsing/setup paths also log. State is the process-global handler and syslog state, not per-session data.

Risks are non-thread-safe handlers, global effects across multiple sessions in one process, retained `va_list` misuse, and format string errors. Test signals include handler install/reset, severity mapping, compile-time format warnings, concurrent logging, syslog enable/close lifetimes, and early setup logs before a session exists.
