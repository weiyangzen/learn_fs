# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/filters.c

Implements sysfs directory filters and scan helpers for NVMe topology discovery.

Filters:
- `libnvme_filter_namespace()`: matches `nvme<id>n<nsid>`.
- `libnvme_filter_paths()`: matches multipath-style `nvme<id>c<ctrl>n<nsid>`.
- `libnvme_filter_ctrls()`: matches controller names `nvme<id>` while excluding namespace/path names.
- `libnvme_filter_subsys()`: matches `nvme-subsys<id>`.

Scanners:
- `libnvme_scan_subsystems()` scans the subsystem sysfs directory.
- `libnvme_scan_subsystem_namespaces()` scans namespaces below a subsystem.
- `libnvme_scan_ctrls()` scans controller sysfs directory.
- `libnvme_scan_ctrl_namespace_paths()` scans path entries below a controller.
- `libnvme_scan_ctrl_namespaces()` scans namespace entries below a controller.
- `libnvme_scan_ns_head_paths()` scans path entries below a namespace head.

Dependencies:
- Uses `scandir` with `alphasort`, private sysfs directory helpers, and accessor getters for sysfs paths.

Risks and tests:
- Filters use `strstr(..., "nvme")` before `sscanf`, so unexpected names containing `nvme` are still parsed but must match the strict format.
- Returned `struct dirent **` arrays are caller-owned and must be freed.
- Tests should feed synthetic dirent names for hidden files, controllers, namespaces, paths, subsystem names, and invalid near-matches.
