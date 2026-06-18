# sources/distributed-fs/xrootd/src/XrdHttpCors/XrdHttpCors.hh

Purpose: Declares the CORS plugin interface for XRootD HTTP.

Important APIs/types/functions: `XrdHttpCors` declares `Configure`, `addAllowedOrigin`, and `getCORSAllowOriginHeader`. The getter type `XrdHttpCorsget_t` describes dynamic loader lookup, and `extern "C" XrdHttpCorsGetHandler` is the concrete plugin entry point.

Control flow: The HTTP layer loads an implementation, calls `Configure` with the config file and error object, adds origins as needed, and asks for an `Access-Control-Allow-Origin` header for a request origin. Returning `std::nullopt` means the origin is not trusted.

State and persistence: Interface only; implementations own origin state in memory.

Dependencies and integration points: Uses `std::optional`, strings, `XrdOucEnv`, `XrdSysError`, and XRootD plugin loading conventions.

Risks: The interface returns a fully formed header string, so callers must avoid adding duplicate header names or CRLF unexpectedly. ABI compatibility depends on C++ standard library and plugin build matching the server.

Test signals: Load handler entry point, configure allowed origins, request both matching and non-matching origins, and verify no CORS header is emitted for untrusted origins.
