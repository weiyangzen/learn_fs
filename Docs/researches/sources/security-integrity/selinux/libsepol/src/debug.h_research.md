# sources/security-integrity/selinux/libsepol/src/debug.h

Purpose: defines libsepol's internal status constants and logging macros. It is the glue between source modules and `debug.c`, giving callers a compact `ERR`, `WARN`, and `INFO` interface while preserving function, channel, and severity metadata.

Important APIs and types: `STATUS_SUCCESS`, `STATUS_ERR`, and `STATUS_NODATA` are local conventional return values. `msg_write(handle_arg, level_arg, channel_arg, func_arg, ...)` selects the supplied handle or falls back to `sepol_compat_handle`, populates message fields, and calls the configured callback. `ERR`, `INFO`, and `WARN` specialize `msg_write` for the `libsepol` channel and `__FUNCTION__`. It declares `sepol_msg_default_handler` and `sepol_compat_handle`.

Control flow: code calls `ERR(handle, ...)`, the macro resolves a handle, tests for `msg_callback`, writes `msg_fname`, `msg_channel`, and `msg_level`, then invokes the callback with the saved callback argument and format string.

State and persistence behavior: no storage is owned by this header, but the macro mutates the selected handle for every emitted message. This is per-handle mutable runtime state rather than persisted policy state.

Dependencies and integration points: includes public `<sepol/debug.h>`, internal `handle.h`, and stdio. It is included by policy parsing, expansion, conversion, record adapters, and utility modules for consistent diagnostics.

Risks: the macro declares a local `_sepol_h`, mutates the handle, and evaluates arguments inside a macro context. The comment correctly flags variable-shadowing concerns. Using a NULL handle intentionally routes to global compatibility state, which can surprise callers in multi-threaded or library-embedded use.

Test signals: compile with GCC format checking, exercise macro calls with NULL and explicit handles, verify no message is emitted when callback is NULL, and test callback metadata under nested or repeated logging paths.
