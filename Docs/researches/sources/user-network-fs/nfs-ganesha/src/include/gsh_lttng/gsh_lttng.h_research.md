# sources/user-network-fs/nfs-ganesha/src/include/gsh_lttng/gsh_lttng.h

Purpose: This header wraps generated LTTng tracepoint macros with Ganesha context fields and no-op fallbacks when tracing is disabled.

Important APIs/types/functions: Under `USE_LTTNG`, `GSH_AUTO_TRACEPOINT` and `GSH_UNIQUE_AUTO_TRACEPOINT` add `__FILE__`, line, function placeholder, `nfs_param.core_param.unique_server_id`, and thread-local `op_ctx->op_id` to trace messages before calling generated macros. Without LTTng, `gsh_empty_function` consumes variadic arguments to avoid unused warnings. Helpers format sessions, verifiers, truncated byte/string/int arrays, and change-info fields.

Control flow: Instrumented code calls the GSH macros. Builds with LTTng emit provider events; builds without LTTng compile argument expressions but perform no tracing.

State and persistence: Trace output is external runtime telemetry. The only read state is global `nfs_param` and thread-local `op_ctx`.

Dependencies and integration points: Depends on `gsh_config.h`, generated `lttng_generator.h`, LTTng tracepoint headers, and NFSv4 constants. Used by general Ganesha trace instrumentation and by transport wrappers.

Risks: Trace arguments may still be evaluated in no-op mode, so expensive or side-effecting expressions are risky. Missing `op_ctx` is handled with op_id zero. Format strings must match generated tracepoint expectations.

Test signals: Build with and without `USE_LTTNG`, verify no unused warnings, emit a trace with and without `op_ctx`, check server/op identifiers, and validate truncated array macros.
