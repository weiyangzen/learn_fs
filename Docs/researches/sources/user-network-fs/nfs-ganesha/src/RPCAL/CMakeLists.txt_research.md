# sources/user-network-fs/nfs-ganesha/src/RPCAL/CMakeLists.txt

Purpose: defines the `rpcal` object library for RPC abstraction layer code: connection management, metrics, duplicate request cache, RPC tools, and optional GSS credential support.

Important APIs and targets: `rpcal_STAT_SRCS`, `add_library(rpcal OBJECT ...)`, `add_sanitizers(rpcal)`, `set_target_properties(... -fPIC)`, feature variables `_HAVE_GSSAPI` and `USE_LTTNG`, and generated trace dependency wiring.

Control flow: builds the base RPCAL source list, appends `gss_credcache.c` and `gss_extra.c` only when GSSAPI support is configured, creates an object library, enables sanitizers, compiles as PIC, and orders LTTng trace header generation when tracing is enabled.

State and persistence: no runtime state; build-time composition controls which RPCAL symbols are available.

Dependencies and integration points: connects RPC transport helpers, duplicate request cache, and connection-manager code into the larger server target. Optional GSS sources must align with headers, Kerberos libraries, and authentication feature gates.

Risks: feature-gate mismatches can produce missing authentication or duplicate symbol/link errors. Since this is an object library, every consumer receives the same object set; compile flags and generated trace dependencies must be correct at this level.

Test signals: configure builds with and without GSSAPI and LTTng, verify final ganesha targets link, and run unit/integration tests covering duplicate requests, connection manager metrics, and GSS startup only in matching builds.
