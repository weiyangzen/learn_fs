# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kdi.h

## Role

`kdi.h` defines the public part of the Kernel/Debugger Interface. It names the debugger virtual-address reservation, declares debugger vector globals, exposes kernel-to-debugger notification wrappers, and defines DTrace/kmdb breakpoint coordination state.

## Major Definitions

`kdi_segdebugbase` and `kdi_segdebugsize` describe the VA range reserved for kmdb. The file forward-declares kernel structures used across KDI and defines opaque `kdi_debugvec_t` and `kdi_t`. `kdi_dvec` points to the debugger callback vector and `kdi_dmods` tracks debugger-visible modules. `KDI_VERSION` is 7.

The DTrace/kmdb coordination model uses `kdi_dtrace_set_t` transition requests for DTrace activate/deactivate and kmdb breakpoint activate/deactivate. `kdi_dtrace_state_t` represents active DTrace, idle, or active kmdb breakpoint states. Comments document that DTrace and kmdb cannot both own breakpoints and transitions do not go directly between active states.

## Interfaces

Notification wrappers include VM-ready, memory-available, module-available, thread-available, module-loaded, and module-unloading calls, with SPARC-only CPU-init and CPR-restart notifications. `kdi_dtrace_set()` requests DTrace/kmdb state transitions.

## Integration Notes

The debugger side of the interface is architecture-specific and defined through `archkdi.h`/machine headers, while this header lets kernel code notify debugger state changes. The functions are intended for stopped-system debugger control paths and breakpoint ownership coordination, so misuse can interfere with DTrace or kmdb operation.
