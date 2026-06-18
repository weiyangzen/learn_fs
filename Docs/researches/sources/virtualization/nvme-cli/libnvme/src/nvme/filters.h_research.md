# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/filters.h

Public declarations for NVMe sysfs filters and scan helpers.

Exports:
- Four `dirent` predicate filters for namespaces, paths, controllers, and subsystems.
- Six scan helpers returning a count or negative errno-style error.

Integration:
- Includes `<dirent.h>` and `<nvme/tree.h>`.
- Implemented by `filters.c`.
- Used by libnvme topology scanning code to enumerate controllers, namespaces, paths, namespace heads, and subsystems.

Contract:
- On success, scan helpers return the number of entries in the caller-provided `struct dirent ***`.
- On failure, they return negative errno.
- Caller owns the `scandir` results.
