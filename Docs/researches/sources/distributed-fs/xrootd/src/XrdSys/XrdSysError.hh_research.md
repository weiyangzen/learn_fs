## sources/distributed-fs/xrootd/src/XrdSys/XrdSysError.hh

Purpose: declares error table types and `XrdSysError`, the logger-backed error-reporting API.

Important APIs/types/functions: `XrdSysError_Table` maps numeric codes to static text; `XrdSysError_Table_Errno` maps extended codes to errno values; log-mask constants `SYS_LOG_01` through `SYS_LOG_08`; `XrdSysError` exposes `addTable()`, `baseFD()`, `ec2text()`, `ec2errno()`, `Emsg()` overloads, `Log()`, `logger()`, `Say()`, `setMsgMask()`, `getMsgMask()`, `SetPrefix()`, `TBeg()`, and `TEnd()`.

Control flow: table lookups are range checks plus array indexing. `Log()` is an inline mask gate before calling `Emsg()`. `logger()` can swap the logger pointer and returns the old one.

State and persistence: global linked lists of registered tables; per-instance prefix pointer/length, message mask, and `XrdSysLogger *`. Tables are not freed by this class and are expected to refer to static text arrays.

Dependencies and integration: forward-declares `XrdSysLogger`; includes C string/platform headers. Used by components that need uniform diagnostics and errno mapping.

Risks: no ownership or synchronization around registered tables, prefixes, or loggers. `ec2errno()` is non-static because it uses registered static state but no instance state.

Test signals: table boundary conditions, multiple table ordering, mask filtering, logger replacement, prefix lifetime assumptions, and compile behavior on Windows and POSIX.
