<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/syslog.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/syslog.hpp

Purpose: `SysLog` wraps system syslog calls with fmt formatting and mergerfs defaults.

Important APIs: `open()` calls `openlog` with ident `mergerfs`, `LOG_CONS|LOG_PID`, and `LOG_USER`; `close()` calls `closelog`. `log(priority, format, args...)` formats a message and passes it as `%s` to `syslog`. Convenience functions map to info, debug, notice, warning, error, alert, and critical priorities.

State and integration: syslog state is process-global. The wrapper is used by fatal errors, thread-pool exception logging, and debug init summaries.

Risks and test signals: formatting happens before syslog, so expensive or throwing format operations occur in the caller context. Tests can inject representative format strings and verify that user-controlled percent signs are safe because syslog receives a fixed `%s` format.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/syslog.hpp -->
