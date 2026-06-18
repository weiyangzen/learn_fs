# File Research: sources/virtualization/nvme-cli/libnvme/test/sysfs/tree-dump.c

## Role

`tree-dump.c` is a small executable that scans libnvme topology and dumps the resulting tree for sysfs fixture tests.

## Behavior

It creates a libnvme context, calls `libnvme_scan_topology()`, tolerates `ENOENT` and `EACCES`, then calls `libnvme_dump_tree()` and prints a trailing newline. It exits success only if scanning and dumping succeed.

The actual sysfs path and host identity are supplied through environment variables by `tree-diff.sh`.

## Dependencies

- Public libnvme topology APIs.
- Standard C errno and process exit APIs.

## Filesystem/Storage Relevance

This directly tests libnvme’s interpretation of NVMe controller, subsystem, namespace, and path state represented in sysfs.
