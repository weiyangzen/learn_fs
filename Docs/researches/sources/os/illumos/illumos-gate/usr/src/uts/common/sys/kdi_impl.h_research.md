# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kdi_impl.h

## Role

`kdi_impl.h` defines the implementation-side Kernel/Debugger Interface structures and helper entry points. It expands the opaque public KDI types into debugger callback vectors, platform claim/release hooks, and the kernel service ops vector consumed by kmdb.

## Major Definitions

`struct kdi_debugvec` is the kernel-to-debugger vector. It includes kernel-control notifications, debugger callbacks for VM/memory/module events, x86 fault handling, and SPARC CPU/CPR callbacks where applicable. `kdi_plat_t` holds platform hooks for system and console claim/release, and macros expose those hooks through the global `kdi_plat` member.

`struct kdi` is the debugger-to-kernel service vector. It records the interface version and operations for module-change detection, module iteration, loaded/change checks, system claim/release, physical reads/writes, cache flushing, non-toxic range checks, polled console I/O acquisition, virtual-to-physical translation, DTrace state get/set, platform callback execution, kmdb entry, plus machine-specific and platform-specific embedded state.

## Interfaces

The file declares softcall/setsoftint helpers, physical read/write wrappers, range toxicity checks, cache flushing, DTrace state query, virtual-to-physical translation, CPU/machine/platform KDI initialization functions, and temporary boot KDI initialization/finalization helpers.

## Integration Notes

Most operations are intended to work while the debugger has stopped the system, so normal blocking services are unavailable. Implementations must avoid allocation and synchronization assumptions that are unsafe in debugger-control context. Architecture conditionals make this header a common contract over machine-specific debugger mechanics.
