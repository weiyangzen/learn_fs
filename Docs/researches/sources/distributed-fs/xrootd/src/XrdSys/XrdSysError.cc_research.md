## sources/distributed-fs/xrootd/src/XrdSys/XrdSysError.cc

Purpose: implements formatted error and trace emission for `XrdSysError`.

Important APIs/types/functions: static tables `XrdSysError::etab` and `etab_errno`; `baseFD()` delegates to `Logger->originalFD()`; `ec2text()` looks up custom error text then falls back to `XrdSysE2T`; `ec2errno()` maps extended codes through registered errno tables; `Emsg()` overloads produce timestamped/prefixed messages; `Say()` emits an unprefixed line; `TBeg()` and `TEnd()` bracket trace output through the logger.

Control flow: formatting is built as `struct iovec` arrays to avoid temporary concatenation. `Emsg(esfx, ecode, ...)` formats "Unable to ..." plus translated error text. The string-only overload and `Say()` conditionally append non-empty fragments.

State and persistence: shared static error tables are process-global and not synchronized for mutation. Each instance owns prefix pointer, prefix length, message mask, and logger pointer but does not own the pointed-to prefix/logger.

Dependencies and integration: depends on `XrdSysE2T`, `XrdSysLogger`, `XrdSysHeaders`, and platform headers. It is the standard diagnostic facade for XrdSys and plugin-loading code.

Risks: `SetPrefix()` calls `strlen()` on the supplied pointer and stores it without copying, so caller lifetime matters. Static table additions must happen before multithreading. Logger must be non-null.

Test signals: custom table lookup, negative error handling, extended errno mapping, prefix changes, null/empty optional fragments, `Log()` mask gating, and trace begin/end serialization.
