<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fatal.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fatal.hpp

Purpose: `fatal::abort` provides a formatted fatal-error path for mergerfs. It formats a message with fmt, writes it to stderr with a `mergerfs: FATAL` prefix, logs it to syslog at critical priority, and calls `std::abort`.

Important APIs and flow: the template accepts `fmt::format_string<Args...>` so format checking happens at compile time where fmt supports it. The function is marked `[[noreturn]]`, which helps callers and optimizers understand control never returns.

State and integration: it depends on `SysLog::crit` and fmt. It does not persist state, but it emits to process stderr and the system logger.

Risks and test signals: this path terminates the process and is unsuitable for recoverable errors. Tests should normally isolate it in a subprocess and assert stderr/syslog formatting and abnormal termination. Formatting failures would be compile-time for literal format strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fatal.hpp -->
