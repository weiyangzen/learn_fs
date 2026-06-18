# File Research: sources/os/bsd/freebsd-src/sys/sys/loginclass.h

Defines per-login-class resource-accounting state.

Key content:
- `struct loginclass` contains list linkage, login class name, reference count, and pointer to resource accounting object `struct racct`.
- Declares `loginclass_hold`, `loginclass_free`, `loginclass_find`, and `loginclass_racct_foreach`.
- `loginclass_racct_foreach` supports callbacks over login-class resource accounting objects with optional pre/post hooks and two generic callback arguments.

Research relevance:
- Provides the kernel representation for login classes used in resource accounting and limits.
- Relevant to filesystem work where credentials, jails, or resource accounting intersect with mount/file operations indirectly.

Cautions:
- Depends on `MAXLOGNAME` and `LIST_ENTRY` being available from including context.
- This header only exposes the structure and lifecycle API; policy and locking live elsewhere.
