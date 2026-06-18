# File Research: sources/os/bsd/freebsd-src/sys/sys/dtrace_bsd.h

## Purpose
Declares FreeBSD shims and hook variables used by DTrace and related providers.

## Main Elements
- Trap hooks: `dtrace_trap_func`, `dtrace_doubletrap_func`.
- pid/return probe hooks and virtual-time switch hook.
- Fasttrap fork/exec/exit hooks.
- malloc probe hook.
- NFS client provider hooks for access cache, attribute cache, and RPC start/done probes across old/new NFS client naming.
- Kernel DTrace private storage sizing and constructor/destructor hooks for proc/thread.
- Time helpers: `dtrace_gethrtime()` and `dtrace_gethrestime()`.

## Dependencies And Integration
Used by DTrace modules, trap handling, fork/exec/exit, malloc, NFS client code, and proc/thread lifecycle code.

## Risk Notes
Most entries are global function pointers invoked from hot or sensitive kernel paths. Registration must ensure null checks, module lifetime safety, and trap recursion avoidance.
