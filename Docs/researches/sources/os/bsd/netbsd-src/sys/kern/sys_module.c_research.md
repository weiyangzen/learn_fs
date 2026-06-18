# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_module.c

## Purpose
Implements `modctl(2)` syscall support for loading, unloading, querying, and compatibility dispatch for kernel modules.

## Main Interfaces
- `sys_modctl`: dispatches `MODCTL_LOAD`, `MODCTL_UNLOAD`, `MODCTL_STAT`, `MODCTL_EXISTS`, and compatibility hooks.
- `handle_modctl_load`: copies a module path and optional property dictionary string, parses properties, and calls `module_load`.
- `handle_modctl_stat`: snapshots active and built-in module metadata into user-provided iovec storage.

## State And Control Flow
Load validates the optional property pointer/length pairing, bounds property input to `MAXPROPSLEN`, copies module path through a pathname buffer, internalizes properties, and releases temporary objects. Stat holds `kernconfig_lock`, counts modules and required-module strings, copies metadata into kernel buffers, unlocks, then copies count, `modstat_t` array, required strings, and final iovec length to userland.

## Dependencies And Integration
Integrates with kernel module lists, kobj stats, kauth kernel-pointer visibility checks, property dictionaries, module autoloading, syscall compatibility hooks, and kernel config locking.

## Risks And Edge Cases
- Kernel object addresses are exposed only when `KAUTH_REQ_PROCESS_CANSEE_KPTR` permits it.
- Output is truncated to the caller's iovec length but reports the full required size back in the iovec.
- Module list size could change after counting only while protected by `kernconfig_lock`.
- Property strings are size-limited to reduce allocation DoS risk.

## Filesystem Relevance
Indirect. Module loading may load filesystem modules, and path copying names a module file, but this file is module-management syscall glue rather than filesystem logic.
