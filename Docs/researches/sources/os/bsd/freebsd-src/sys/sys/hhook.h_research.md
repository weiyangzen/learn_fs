# File Research: sources/os/bsd/freebsd-src/sys/sys/hhook.h

Defines the FreeBSD helper hook KPI used by Khelp modules to register callback hooks at named kernel hook points. It declares hook types for TCP, socket, and IPsec paths; registration flags for sleep behavior and VNET-local hook heads; and the `hhook_func_t` callback signature.

Core data structures are `struct hookinfo`, carrying callback/helper/user-data/type/id registration metadata, and `struct hhook_head`, carrying the hook queue, rmlock, type/id, VNET id, hook count, refcount, and global/VNET list links. Public routines support adding/removing hooks directly or by lookup, registering/deregistering hook heads, acquiring/releasing heads, testing virtualization, and running hooks.

The `HHOOKS_RUN_IF` and `HHOOKS_RUN_LOOKUP_IF` macros are important performance and correctness wrappers: the former avoids entering hook dispatch when no hooks are registered, while the latter performs lookup/refcount/release around infrequent call sites.
