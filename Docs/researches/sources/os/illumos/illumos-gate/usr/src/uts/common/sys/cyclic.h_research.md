# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cyclic.h

Public kernel interface for the cyclic subsystem, illumos's high-resolution cyclic timer/callback facility. It defines cyclic levels, IDs, handler/time descriptors, omni-cyclic handlers, and lifecycle/CPU-migration APIs.

Key elements:
- Defines three execution levels: low, lock, and high, with two software interrupt levels.
- Defines cyclic ID/index/cookie/level types, handler function type, backend argument type, and `CYCLIC_NONE`.
- `cyc_handler_t` stores callback function, argument, and desired cyclic level.
- `cyc_time_t` stores absolute first-fire time and interval.
- `cyc_omni_handler_t` describes callbacks used to create/remove per-CPU cyclics as CPUs come online/offline.
- `CY_INFINITY` represents an unbounded time value.
- Kernel/fake-kernel APIs add/remove cyclics, add omni-cyclics, bind/reprogram/move cyclics, get timer resolution, handle CPU online/offline/juggle/move events, suspend/resume, and dispatch high/soft cyclic interrupts.

Dependencies:
- Includes time, CPU, and CPU partition definitions for non-assembly consumers.
- Implemented by the cyclic subsystem and platform-specific cyclic backend.

Research notes:
- The level model is central: callbacks may run at high interrupt, lock-level soft interrupt, or low-level soft interrupt context.
- Omni-cyclics abstract per-CPU timer setup and teardown across CPU hotplug.
