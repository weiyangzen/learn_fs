# sources/security-integrity/selinux/libsepol/include/sepol/debug.h

Purpose: Declares public libsepol messaging and legacy debug controls.

Important APIs and symbols: Defines message levels `SEPOL_MSG_ERR`, `SEPOL_MSG_WARN`, `SEPOL_MSG_INFO`; exports deprecated `sepol_debug`, getters for message level/channel/file name, and `sepol_msg_set_callback` with printf-style callback annotation.

Control flow: Callers install or suppress a callback on a `sepol_handle_t`; internal `ERR/WARN/INFO` macros route diagnostics through that handle.

State and persistence: Callback pointer and argument live in the handle. Deprecated debug state is process-global compatibility behavior.

Dependencies and integration points: Central to diagnostics across policydb parsing, linking, context conversion, and record APIs.

Risks: Passing NULL suppresses messages, which can hide parse causes. Callback format handling must remain ABI-compatible and variadic-safe.

Test signals: Error-path tests with custom callbacks should observe expected level/channel/file metadata and formatted messages.
