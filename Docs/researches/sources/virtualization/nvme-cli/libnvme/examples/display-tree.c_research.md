# File Research: sources/virtualization/nvme-cli/libnvme/examples/display-tree.c

This C example scans NVMe topology and prints it as an ASCII tree.

Core behavior:
- Creates a global context and scans topology.
- Iterates hosts, subsystems, subsystem namespaces, controllers, controller namespaces, and controller paths.
- Prints selected attributes: subsystem NQN, namespace LBA size/count, controller transport/address/state, and path ANA state.
- Uses `_safe` iterator variants where next pointers are needed for tree branch formatting.

Integration role:
- Demonstrates topology walking and tree-style presentation with libnvme.
