# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiLogger.hh

Purpose: declares the SSI logging facade exposed to provider/service code. It abstracts direct XRootD logger calls and supports application-defined message callbacks.

Important APIs/types: static methods are `Msg()`, `Msgf()`, `Msgv()` with `va_list`, `Msgv(iovec *, int)`, `SetMCB()`, `TBeg()`, and `TEnd()`. `MCB_t` defines callback signature with timestamp, thread ID, message pointer, and length. `mcbType` selects all/client/server callback installation. Macros `SSI_LOG` and `SSI_SAY` wrap stream output.

Control flow and state: the class itself stores no instance data; all behavior is static and implemented in the `.cc`. The callback API is intended to be called during static initialization. Header comments define an alternate plugin-level `XrdSsiLoggerMCB` pointer for server-side log routing.

Dependencies and integration: depends on `<cstdarg>` and forward-declared `iovec`; implementation depends on XRootD logging. Risks include global initialization ordering, callback lifetime, and the `SSI_LOG`/`SSI_SAY` macro references spelling `XrdSSiLogger` instead of `XrdSsiLogger`, which would fail if those macros are compiled as written. Test signals should compile macro users, install callbacks in each mode, and verify varargs truncation behavior.
