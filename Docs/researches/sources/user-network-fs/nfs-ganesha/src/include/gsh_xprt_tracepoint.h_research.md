# sources/user-network-fs/nfs-ganesha/src/include/gsh_xprt_tracepoint.h

Purpose: This header adds transport-aware wrappers around the generic Ganesha LTTng tracepoint macros.

Important APIs/types/functions: `GSH_XPRT_AUTO_TRACEPOINT` and `GSH_XPRT_UNIQUE_AUTO_TRACEPOINT` prepend `XPRT_FMT` and `XPRT_VARS(_xprt)` to the caller's format/arguments, then delegate to `GSH_AUTO_TRACEPOINT` or `GSH_UNIQUE_AUTO_TRACEPOINT`.

Control flow: RPC transport code calls these macros when logging events tied to an `SVCXPRT`. The lower GSH tracepoint layer supplies server/op IDs and LTTng/no-op behavior.

State and persistence: It stores no state. Trace output captures runtime transport metadata extracted from the transport argument.

Dependencies and integration points: Includes `gsh_lttng/gsh_lttng.h` and `rpc/svc.h`; relies on ntirpc-provided `XPRT_FMT` and `XPRT_VARS` macros.

Risks: `_xprt` must be valid for `XPRT_VARS`. Format and argument ordering must remain aligned after macro expansion. No include guard is present in the file, so repeated inclusion relies on the idempotence of included macros and definitions.

Test signals: Compile transport tracing call sites, build with/without LTTng, emit traces with TCP/RDMA/local transports, validate format fields, and test null/invalid transport avoidance at call sites.
