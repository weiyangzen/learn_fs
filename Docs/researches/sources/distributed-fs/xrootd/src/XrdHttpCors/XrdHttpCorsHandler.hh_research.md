# sources/distributed-fs/xrootd/src/XrdHttpCors/XrdHttpCorsHandler.hh

Purpose: Declares the default `XrdHttpCorsHandler` implementation.

Important APIs/types/functions: Inherits `XrdHttpCors`, overrides `Configure`, `addAllowedOrigin`, and `getCORSAllowOriginHeader`, and stores origins in `std::unordered_set<std::string> m_origins`.

Control flow: The header only defines the object shape used by the implementation and loader.

State and persistence: Per-plugin instance in-memory origin set. No persistence.

Dependencies and integration points: Includes the CORS interface and standard unordered set. Used by `XrdHttpCorsHandler.cc`.

Risks: The data structure is not explicitly synchronized; safety depends on configure-before-use or external locking if runtime origin changes are introduced.

Test signals: Compile with C++17 optional support, instantiate handler, add origins, and query allowed/non-allowed values.
