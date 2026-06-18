# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSiteName.hh

Purpose: declares the one-method `XrdOucSiteName` utility for setting a sanitized XRootD site name.

Important APIs, types, and functions: `static const char *Set(const char *name, int maxlen=15)` is the only functional API. Constructor and destructor are trivial.

Control flow: users call `Set()` during configuration or process initialization; implementation handles normalization and environment export.

State and persistence: no object state exists. Side effects are process-environment state managed by the implementation.

Dependencies and integration points: the header has no includes and integrates with any code wanting to publish `XRDSITE` without depending directly on `XrdOucEnv` in the caller.

Risks and test signals: callers must understand the returned pointer lifetime follows environment export behavior. Tests should compile the header standalone and verify default maximum length through the `.cc`.
