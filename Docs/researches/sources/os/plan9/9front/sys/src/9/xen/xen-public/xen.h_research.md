# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/xen.h

Purpose: Core Xen public guest ABI header. It selects architecture-specific ABI headers, defines guest handles for primitive types, hypercall numbers, compatibility remaps, virtual IRQs, MMU update commands, VA mapping flags, console/vm-assist commands, domain IDs, multicall entries, event-channel shared state, time/shared-info structures, start-of-day boot layout, dom0 VGA console info, and helper typedefs/macros.

Key interfaces:
- Hypercall numbers `__HYPERVISOR_*`.
- VIRQ constants and `NR_VIRQS`.
- `mmuext_op`, `mmu_update`, `multicall_entry`.
- `vcpu_time_info`, `vcpu_info`, `shared_info`, `start_info`.
- Domain IDs: `DOMID_SELF`, `DOMID_IO`, `DOMID_XEN`, `DOMID_COW`, `DOMID_INVALID`, `DOMID_IDLE`.
- `xenctl_bitmap` for tool/sysctl use.

Integration notes: Central dependency for the other Xen public headers and Plan 9 Xen kernel code. `xensystem.c` uses hypercall numbers, MMU constants, event-channel state, domain IDs, and `start_info/shared_info`.

Risk/attention points: It mixes architecture selection, ABI constants, and shared-memory layouts. Any local type mismatch can break hypercall marshalling.
