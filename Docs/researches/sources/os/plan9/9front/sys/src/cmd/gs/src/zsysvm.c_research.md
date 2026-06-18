# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zsysvm.c

## Purpose
Adds non-standard Ghostscript operators for creating arrays, dictionaries, packed arrays, and strings in a selected VM space.

## Key Elements
Uses `specific_vm_op()` to temporarily switch allocation space around existing constructors. Exposes `.globalvmarray`, `.globalvmdict`, `.globalvmpackedarray`, `.globalvmstring`, corresponding local/system variants, and `.systemvmcheck`.

## Behavior/Risks
System VM is described as outside normal `save`/`restore` semantics and restricted to simple/system references. The implementation saves and restores the current allocator space around each delegated constructor, so failures propagate from the underlying `zarray`, `zdict`, `zpackedarray`, or `zstring`.

## Dependencies
Depends on VM-space allocation state from `ialloc.h`/`ivmspace.h`, generic constructors declared elsewhere, and ref-space checks from `store.h`.
