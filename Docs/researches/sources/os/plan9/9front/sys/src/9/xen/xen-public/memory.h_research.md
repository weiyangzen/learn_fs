# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/memory.h

Purpose: Xen public memory-management ABI header. It defines `HYPERVISOR_memory_op` command numbers and payload layouts for reservation changes, physical map updates, machine memory maps, populate-on-demand targets, paging/access/sharing operations, and memory claims.

Key interfaces:
- `xen_memory_reservation`, `xen_memory_exchange`, `xen_machphys_mfn_list`, `xen_machphys_mapping`.
- `xen_add_to_physmap`, `xen_add_to_physmap_range`, `xen_remove_from_physmap`.
- `xen_memory_map`, `xen_foreign_memory_map`, `xen_pod_target`.
- Tool/hypervisor-only event/sharing structs under `__XEN__ || __XEN_TOOLS__`.

Integration notes: Included by Xen-facing kernel code that needs allocation/deallocation or grant/foreign mapping semantics. This 9front tree uses `XENMEM_decrease_reservation` in `xensystem.c` when donating a frame.

Risk/attention points: This is an ABI contract; field widths, guest-handle macros, and interface-version conditionals must remain in sync with the Xen headers expected by the hypervisor.
