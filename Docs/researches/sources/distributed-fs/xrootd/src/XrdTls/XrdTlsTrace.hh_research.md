# sources/distributed-fs/xrootd/src/XrdTls/XrdTlsTrace.hh

Purpose: Defines TLS tracing macros for context, socket, and socket I/O operations.

Important APIs/types/functions: When NODEBUG is not set, includes XrdSysTrace.hh and defines TRACING(act), DBG_CTX(y), DBG_SOK(y), DBG_SIO(y), DBG_TLS(y), and EPNAME(x). NODEBUG builds define no-op debug macros.

Control flow: Call sites set EPNAME at function scope and then use DBG_* macros. The macros check XrdTlsGlobal::SysTrace.What against XrdTls debug flags and emit SYSTRACE records with either no trace id for context or pImpl->traceID for socket operations.

State/persistence: No state owned here. Depends on process-global XrdTlsGlobal::SysTrace and ambient pImpl/epname symbols in calling scope.

Dependencies/integration: Coupled to XrdTls.hh debug flags and XrdTls.cc global trace object. Used heavily by XrdTlsContext.cc and XrdTlsSocket.cc.

Risks: Macro context is implicit; DBG_SOK/DBG_SIO/DBG_TLS require pImpl. TRACING lacks parentheses around the full expression, so callers should use it carefully in larger expressions.

Test signals: Build with and without NODEBUG, enable XRDTLS_DEBUG=ctx/sok/sio/all for client contexts, and verify traces are emitted without altering TLS behavior.
