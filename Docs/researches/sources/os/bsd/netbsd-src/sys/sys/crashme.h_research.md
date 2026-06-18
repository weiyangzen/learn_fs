# File Research: sources/os/bsd/netbsd-src/sys/sys/crashme.h

Declares the kernel crashme node registration interface used for controlled crash/panic testing hooks.

Key content:
- `crashme_fn` callback type returning `int`.
- `struct crashme_node` stores short name, long name, callback, sysctl id, and linked-list pointer.
- APIs: `crashme_add`, `crashme_remove`.

Important behavior:
- Comments explicitly avoid marking callbacks `__dead`; crashme failures should return to the caller so setup or errors can be handled.
- Callback returns zero on success and nonzero when plain `panic()` should be called.
