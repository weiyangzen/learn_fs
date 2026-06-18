# File Research: sources/os/bsd/netbsd-src/sys/sys/pset.h

## Purpose
Defines processor set userland API constants and kernel initialization/state declarations.

## Main API
- Special IDs: `PS_NONE`, `PS_MYID`, `PS_QUERY`.
- Userland calls: `pset_assign`, `pset_bind`, `pset_create`, `pset_destroy`.
- NetBSD extension: `_pset_bind`.
- Kernel type: `pset_info_t`.
- Kernel function: `psets_init`.

## Dependencies
Uses feature-test macros, basic types, and `idtype_t`.

## Risks and Notes
The public API exposes processor-set IDs and binding by id type. Kernel `pset_info_t` is currently minimal, so most behavior is in implementation code.
