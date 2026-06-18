# sources/sync-backup/restic/internal/walker/walker.go

Purpose: depth-first traversal of restic tree blobs with callback control.

Important APIs/types/functions: `ErrSkipNode`, `WalkFunc`, `WalkVisitor`, exported `Walk()`, and recursive helper `walk()`.

Control flow: `Walk()` loads the root tree and calls `ProcessNode` for `/` with any root-load error. If the root callback returns `ErrSkipNode`, traversal stops without error. `walk()` iterates tree nodes, validates node type, calls `ProcessNode`, supports `ErrSkipNode` to skip a directory or remaining siblings for non-directories, loads directory subtrees before callback, recurses, and calls optional `LeaveDir`.

State and persistence: no persistent state; traversal is streaming through `data.TreeNodeIterator`. Context cancellation is checked during iteration.

Dependencies/integration: depends on `internal/data`, `internal/restic`, `github.com/pkg/errors`, and path joining.

Risks: directory subtree load errors are passed to the callback along with the node; callback policy determines whether to continue. A nil directory subtree or invalid node type is fatal.

Test signals: `walker_test.go` covers traversal order, parent tree IDs, skip behavior, errors, and leave callbacks.
