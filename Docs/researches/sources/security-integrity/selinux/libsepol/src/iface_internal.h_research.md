# sources/security-integrity/selinux/libsepol/src/iface_internal.h

Purpose: private include shim for network interface record and collection APIs.

Important APIs and types: includes `<sepol/iface_record.h>` and `<sepol/interfaces.h>` under an internal include guard. No additional declarations are introduced.

Control flow: none.

State and persistence behavior: none.

Dependencies and integration points: used by `iface_record.c` and `interfaces.c` to share public interface declarations.

Risks: minimal; it is compile-time include plumbing.

Test signals: compile interface record and adapter modules against public headers.
