# File Research: sources/virtualization/nvme-cli/libnvme/test/zns.c

This file is a hardware/topology-oriented ZNS diagnostic test. It scans the NVMe topology and prints Zoned Namespace properties for namespaces whose command set identifier is `NVME_CSI_ZNS`.

Core flow:
- `main()` creates a global context, calls `libnvme_scan_topology(ctx, NULL, NULL)`, tolerates `-ENOENT` and `-EACCES`, and walks hosts, subsystems, controllers, and namespaces.
- It checks both controller namespaces and subsystem namespaces.
- `show_zns_properties(libnvme_ns_t n)` obtains a transport handle, allocates a 4 KiB zone report buffer, issues ZNS identify namespace/controller commands, prints fields, issues report zones, prints `nr_zones`, and frees the buffer.

APIs used:
- Tree traversal macros: `libnvme_for_each_host`, `libnvme_for_each_subsystem`, `libnvme_subsystem_for_each_ctrl`, `libnvme_ctrl_for_each_ns`, `libnvme_subsystem_for_each_ns`.
- ZNS command initializers: `nvme_init_zns_identify_ns()`, `nvme_init_zns_identify_ctrl()`, `nvme_init_zns_report_zones()`.
- Passthrough executors: `libnvme_exec_admin_passthru()`, `libnvme_exec_io_passthru()`.
- Endian conversion helpers for ZNS fields.

Integration:
- Meson builds `test-zns`; it is not a pure unit test because it depends on system topology and permissions.

Risk and maintenance notes:
- The zone report allocation size is fixed at `0x1000`, enough for a small report but not exhaustive.
- Failures mostly print diagnostics and return from the per-namespace function rather than failing the program.
