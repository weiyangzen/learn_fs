# sources/security-integrity/selinux/libsemanage/src/direct_api.h

Purpose: declares the internal direct-store backend entry points and direct handle extension.

Important APIs/types/functions: `struct semanage_direct_handle` stores active and transaction lock file descriptors; declares `semanage_direct_connect`, `semanage_direct_is_managed`, `semanage_direct_access_check`, and `semanage_direct_mls_enabled`.

Control flow: handle connection code selects the direct backend, allocates direct state, acquires locks as needed, and dispatches through the direct policy table implemented in `direct_api.c`.

State and persistence behavior: the direct handle tracks lock file descriptors protecting active store and transaction state. Persistent behavior is implemented in the direct backend's sandbox, module, and commit functions.

Dependencies and integration points: included by handle internals and `direct_api.c`. It is the direct backend counterpart to the public store selection API.

Risks: lock descriptor lifecycle must match connect/disconnect and transaction boundaries. Test signals include is-managed checks, access checks, lock release on disconnect, and MLS detection.
