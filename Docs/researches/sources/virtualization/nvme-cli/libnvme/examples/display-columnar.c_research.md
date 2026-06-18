# File Research: sources/virtualization/nvme-cli/libnvme/examples/display-columnar.c

This C example scans NVMe topology and prints hosts/subsystems/controllers/namespaces in columnar format.

Core behavior:
- Creates a global context and scans topology.
- Prints subsystem name, subsystem NQN, and controller list.
- Prints controller details including serial, model, firmware, transport, address, subsystem, and namespaces.
- Prints namespace details including name, NSID, LBA count, LBA size, and controllers.
- Traverses hosts, subsystems, controllers, namespaces, and paths via libnvme iterator macros.

Integration role:
- Demonstrates libnvme topology traversal and getter APIs in a compact report-style output.
