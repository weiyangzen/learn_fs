# sources/security-integrity/selinux/libsepol/src/handle.h

Purpose: defines the internal layout of `struct sepol_handle` behind the public opaque handle type.

Important APIs and types: `struct sepol_handle` contains transient message metadata (`msg_level`, `msg_channel`, `msg_fname`), a printf-style message callback and callback argument, and expansion flags `disable_dontaudit`, `expand_consume_base`, and `preserve_tunables`.

Control flow: none; the header provides fields consumed by `debug.c`, `debug.h`, `handle.c`, and expansion logic.

State and persistence behavior: instances are heap-allocated by `sepol_handle_create` or statically allocated for compatibility in `debug.c`. Message fields are overwritten during logging; option fields persist on the handle.

Dependencies and integration points: includes public `<sepol/handle.h>` for the opaque typedef. It is the internal contract between public handle APIs, message handling, and policy expansion.

Risks: any ABI-exposed misuse of the internal struct would couple callers to private fields, but the header is internal. Shared handles are not thread-safe for message metadata updates. Callback format attributes only apply under GCC.

Test signals: compile users of internal handle fields, verify callback format warnings, and exercise handle options through expansion and logging paths.
