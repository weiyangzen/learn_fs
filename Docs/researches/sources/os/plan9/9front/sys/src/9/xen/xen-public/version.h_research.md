# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/version.h

Purpose: Xen public version-query ABI. It defines `HYPERVISOR_xen_version` command IDs and result structures.

Key interfaces:
- `XENVER_version`, `XENVER_extraversion`, `XENVER_compile_info`, `XENVER_capabilities`, `XENVER_changeset`, `XENVER_platform_parameters`, `XENVER_get_features`, `XENVER_pagesize`, `XENVER_guest_handle`, `XENVER_commandline`.
- Types for compile info, capabilities, changeset, platform parameters, feature submaps, and command line.

Integration notes: Includes `features.h`. 9front uses `HYPERVISOR_xen_version(0, 0)` as a harmless hypercall to provoke pending event delivery after unmasking.

Risk/attention points: Most commands return zero on success, but `XENVER_version` and `XENVER_pagesize` return direct values.
