# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTrace.hh

Purpose: declares a lightweight tracing helper that wraps an `XrdSysError` destination and a bitmask of enabled trace classes.

Important APIs, types, and functions: `Beg()` and `End()` forward trace context calls to `XrdSysError`. `Tracing(mask)` checks `mask & What`. `What` is public for direct bitmask configuration. Static `bin2hex()` formats binary data for logs.

Control flow: components instantiate a trace object with an error route, update `What`, test `Tracing()` before expensive trace construction, and bracket trace records with `Beg()`/`End()`.

State and persistence: state is the error destination pointer and `What` mask. There is no ownership or persistence.

Dependencies and integration points: includes `XrdSysHeaders.hh` and `XrdSysError.hh`. It integrates with XRootD's logging/tracing infrastructure.

Risks and test signals: `Beg()`/`End()` assume `eDest` is non-null. Public mutable `What` is simple but unsynchronized. Tests should verify null handling expectations, mask checks, and trace forwarding with a fake `XrdSysError`.
