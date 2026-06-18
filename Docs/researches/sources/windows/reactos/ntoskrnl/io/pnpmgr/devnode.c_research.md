# File Research: sources/windows/reactos/ntoskrnl/io/pnpmgr/devnode.c

This file implements basic PnP device tree storage operations: root globals, devnode allocation/freeing, parent/child/sibling insertion, state and problem mutation, and depth-first traversal.

Core data:
- `IopRootDeviceNode` is the global tree root.
- `IopDeviceTreeLock` protects parent/child/sibling and state-history mutation.
- `IopNumberDeviceNodes` tracks allocated nodes.

Implemented routines:
- `IopGetDeviceNode` returns the devnode stored in a device object's extension.
- `PipAllocateDeviceNode` allocates and zeroes a nonpaged `DEVICE_NODE`, initializes bus fields to undefined/-1, sets `DeviceNodeUninitialized`, initializes arbiter/translator/notification/dock/interface lists, links a supplied PDO through `IoGetDevObjExtension`, and clears `DO_DEVICE_INITIALIZING`.
- `PiInsertDevNode` inserts a node as the last child of a parent under `IopDeviceTreeLock`, updates `Parent`, `Sibling`, `Child`, `LastChild`, and sets `Level`.
- `PiSetDevNodeState` changes state under the tree lock, records previous state, and stores previous states in the circular `StateHistory`.
- `PiSetDevNodeProblem` and `PiClearDevNodeProblem` set/clear `DNF_HAS_PROBLEM` and the config-manager problem code.
- `IopFreeDeviceNode` asserts the node is childless, removed, and has no target notifications, unlinks it from parent/sibling lists, frees `InstancePath`, `ServiceName`, resource lists, resource requirements, and boot resources, clears the PDO extension's devnode pointer, and frees the node.
- `IopTraverseDeviceTree` performs depth-first traversal from `FirstDeviceNode`, references each PDO while the action runs, advances using `IopFindNextDeviceNodeForTraversal`, and treats action-returned `STATUS_UNSUCCESSFUL` as a clean stop.

Inactive code:
- A large `#if 0` `IopCreateDeviceNode` implementation remains as historical/disabled code for legacy root device creation and registry setup. The live path uses `PipAllocateDeviceNode`, root bus helpers, and explicit initialization elsewhere.

Integration points:
- `devaction.c` uses this file for allocation, insertion, state changes, problem codes, and traversal-stable references.
- `plugplay.c` uses `IopTraverseDeviceTree` to find device instances and reads tree links for parent/child/sibling queries.
- `pnpinit.c` creates the root device node through `PipAllocateDeviceNode`.

Research notes:
- The tree uses a simple first-child/last-child/sibling layout, so removal must update both parent child pointers and prior sibling links correctly.
- Traversal intentionally keeps a PDO reference so callbacks can tolerate node deletion, but comments note this is a hack compared with a stricter child-before-parent deletion model.
- `IopNumberDeviceNodes` increments on allocation but this file does not decrement it during free.
