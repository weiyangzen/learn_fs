<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/xlog.h -->
# sources/user-network-fs/rpcbind/src/xlog.h

Purpose: Declares logging severity/debug masks, the debug facility name mapping structure, and the xlog API used by rpcbind source files.

Important APIs, types, and functions: Defines severity masks `L_FATAL`, `L_ERROR`, `L_WARNING`, `L_NOTICE`, and `L_ALL`, plus debug masks `D_GENERAL`, `D_CALL`, `D_AUTH`, `D_FAC3` through `D_FAC7`, `D_PARSE`, and `D_ALL`. Declares `struct xlog_debugfac`, `export_errno`, and all xlog functions.

Control flow and integration: Callers open the logging system with `xlog_open`, choose stderr/syslog outputs, enable facilities with numeric or string config functions, check debug state with `xlog_enabled`, and log through severity wrappers. `xlog_err` and `xlog_errno` are fatal through the implementation.

State and persistence: The header exposes only `export_errno`; all other state is internal to `xlog.c`. No persistence contract.

Dependencies: Requires `<stdarg.h>` because `xlog_backend` accepts a `va_list`.

Risks: The comment warns that callers should not OR debug and severity classes together; the numeric layout makes misuse possible. `L_FATAL` exits, so using it in reusable or cleanup-sensitive code changes process control flow.

Test signals: Compile coverage plus runtime tests for each macro class and wrapper function. Static analysis can catch accidental OR combinations or fatal wrapper use in paths expected to return.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/xlog.h -->
