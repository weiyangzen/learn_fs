# sources/storage-engines/pebble/internal/treesteps/tree_steps_on.go

## Purpose
This invariants-only file implements live treesteps recording. It captures snapshots of a tree before, during, and after operations on nodes, including node properties, children, hidden children, and active operation annotations.

## Important APIs, Types, and Functions
`Enabled = true`. `StartRecording(root,name,opts...)` creates a `Recording` with default max depths and records the initial tree. `MaxTreeDepth` and `MaxOpDepth` adjust recording limits. `NodeUpdated` emits update steps for nodes in active recordings. `NodeInfof`, `AddPropf`, and `AddChildren` describe nodes. `Recording.Finish` clears node ownership and returns `Steps`. `IsRecording` checks active node participation. `StartOpf`, `Op.Updatef`, `UpdateLastOpf`, and `Op.Finishf` manage operation annotations and steps. `TreeToString` renders current state without recording. Internals include global mutex state, `nodeState`, `buildTree`, and `nodeStateLocked`.

## Control Flow and State
A global mutex and atomic flag coordinate all recordings. Starting a recording initializes or reuses the global node map and immediately builds an initial tree. `buildTree` calls each node's `TreeStepsNode`, records node state ownership, captures active ops, and recurses until `maxTreeDepth`, marking hidden children if truncated. Operations are tracked per node; starts and updates emit intermediate steps unless at the max op depth, and finish always emits a final step then removes the op. `Finish` removes all node states for the recording and clears the global active flag if no recordings remain. No disk persistence exists.

## Dependencies and Integration
It uses `fmt`, `reflect`, `slices`, `strings`, `sync`, `sync/atomic`, `unicode`, and Cockroach errors. It integrates with `data.go` for output and with any Pebble data structure implementing `TreeStepsNode`.

## Risks and Edge Cases
The global node map prevents the same node from participating in multiple recordings and panics if violated. Calls into `TreeStepsNode` happen while holding the global mutex, so implementations must avoid reentrant treesteps calls or blocking work. The package is for debug builds; production builds get no-ops. Nil pointer child handling is explicit in `AddChildren`, but passthrough nodes can remap identity through `NodeInfo.node`.

## Test Signals
`tree_steps_test.go` validates segment tree recordings, depth limits, operation updates, URL output, and passthrough node behavior when built with invariants.
