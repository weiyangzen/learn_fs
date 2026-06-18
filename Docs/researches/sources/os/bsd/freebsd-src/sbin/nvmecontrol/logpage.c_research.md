# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/logpage.c

Implements `nvmecontrol logpage`, common log-page readers, built-in log-page formatters, and the log-page plugin registry.

Key behaviors:
- Registers `logpage` command with options for binary, hex, page ID, LSP, LSI, RAE, vendor formatter, and target device.
- Maintains a sorted SLIST of `struct logpage_function` entries populated by `NVME_LOGPAGE` constructor macros from core and vendor modules.
- Provides `read_logpage()` using `NVME_OPC_GET_LOG_PAGE` passthrough command with NUMD, RAE, LSP, LSI, LPO, CSI, OT, and UUID index fields.
- Supports raw binary output, hex output, or pretty printers.
- Built-in printers include error information, SMART/health, firmware slots, changed namespace list, command effects, reservation notification, sanitize status, and device self-test status.
- Computes variable error log size from controller `elpe`.
- Restricts namespace-level log access to per-namespace SMART when supported.

Research notes:
- Vendor modules extend this registry dynamically or at link/load time.
- Unknown log pages fall back to hex output with default size.
