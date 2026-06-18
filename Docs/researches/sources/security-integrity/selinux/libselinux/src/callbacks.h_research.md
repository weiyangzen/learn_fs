# sources/security-integrity/selinux/libselinux/src/callbacks.h

Purpose: This header declares libselinux callback globals and defines the thread-safe `selinux_log()` macro used throughout the library.

Important APIs/types/functions: declarations cover log, audit, validation, setenforce, and policyload callback pointers plus `log_mutex`. The `selinux_log(type, ...)` macro saves `errno`, locks `log_mutex`, calls `selinux_log_direct`, unlocks, and restores `errno`.

Control flow: code using `selinux_log()` gets serialized output and avoids accidental errno clobbering from logging callbacks. Other callback pointers are consumed directly by label and AVC paths.

State and persistence: exposes process-global callback pointer state owned by `callbacks.c`.

Dependencies and integration: includes public libselinux headers and internal `selinux_internal.h`; used by most modules for diagnostics and validation.

Risks and test signals: callback direct calls outside `selinux_log()` will not get errno preservation. Tests should verify the macro is safe when callback writes to errno and that recursive logging does not deadlock under callback behavior.
