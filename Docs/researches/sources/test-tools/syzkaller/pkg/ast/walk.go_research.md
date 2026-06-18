# sources/test-tools/syzkaller/pkg/ast/walk.go

## Purpose
Implements AST traversal helpers and per-node child walking.

## Important APIs, Types, and Functions
`(*Description).Walk`, `Recursive`, `PostRecursive`, and each node's private `walk` method define traversal. Recursive traversal can be pre-order with pruning or post-order without pruning.

## Control Flow
Top-level `Walk` visits only description nodes. `Recursive` wraps a callback so returning true descends into children. `PostRecursive` descends first, then calls callback. Node walk methods enumerate direct children in structural order.

## State and Persistence Behavior
Pure in-memory traversal with caller-supplied callbacks. No mutation unless callbacks mutate nodes.

## Dependencies and Integration Points
Used by AST analysis/transformation code and parser tests.

## Risks and Test Signals
Risks include omitted new child fields and recursion cycles if future nodes introduce backreferences. `TestParseAll` compares recursive and post-recursive counts.
