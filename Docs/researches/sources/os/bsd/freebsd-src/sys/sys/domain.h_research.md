# File Research: sources/os/bsd/freebsd-src/sys/sys/domain.h

## Purpose
Defines networking protocol domain registration structures and kernel domain add/remove hooks.

## Main Elements
- `struct domain` contains list linkage, address family, protocol switch count/name, flags, optional probe, routing table attach/detach hooks, and flexible `protosw` array.
- Domain flag `DOMF_UNLOADABLE`.
- Kernel exports domain initialization status and global domain list.
- `domain_add()` and `domain_remove()` manage registered domains.
- `DOMAIN_SET()` creates SYSINIT/SYSUNINIT registration for a domain.

## Dependencies And Integration
Used by protocol families, routing table setup, VIMAGE virtual network initialization, and network stack domain discovery.

## Risk Notes
Protocol domain arrays and routing hooks are core network ABI inside the kernel. Module unloadability requires careful teardown ordering.
