# sources/security-integrity/selinux/libsepol/src/debug.c

Purpose: implements libsepol's internal and compatibility message handling. It backs the deprecated process-global debug switch, exposes current message metadata, provides the default stdout/stderr printer, and installs per-handle callbacks used by `ERR`, `WARN`, and `INFO` in `debug.h`.

Important APIs and functions: `sepol_compat_handle` is the fallback global handle for legacy callers. `sepol_debug(int on)` toggles the fallback callback. `sepol_msg_get_level`, `sepol_msg_get_channel`, and `sepol_msg_get_fname` read the transient message fields on a `sepol_handle_t`. `sepol_msg_default_handler` selects `stderr` for errors/warnings and `stdout` for info, prefixes output with channel and function name, then prints a printf-format message. `sepol_msg_set_callback` replaces the callback and callback argument on a handle.

Control flow: `msg_write` in the header populates `msg_fname`, `msg_channel`, and `msg_level` on the selected handle, then invokes the callback. The default callback reads those fields through the getters, chooses the stream, performs `vfprintf`, and appends a newline. The deprecated `sepol_debug` path only changes whether the compatibility handle has a callback.

State and persistence behavior: no durable persistence. State is held in mutable `sepol_handle_t` fields and the global `sepol_compat_handle`. The message metadata fields are overwritten for each emitted message and are not thread-local.

Dependencies and integration points: depends on internal `handle.h` and `debug.h`, plus stdio/varargs. It is used by nearly every libsepol module through logging macros and by public handle setup code through `sepol_msg_set_callback`.

Risks: the compatibility handle and per-handle transient message fields make concurrent logging on a shared handle racy. `sepol_msg_get_*` assumes a non-NULL handle. Custom callbacks must obey the printf format contract and should not assume message metadata survives after the call.

Test signals: verify error and warning messages go to `stderr`, info goes to `stdout`, callback disabling suppresses output, custom callbacks receive the expected level/channel/function fields, and legacy `sepol_debug(0/1)` only affects the compatibility handle.
