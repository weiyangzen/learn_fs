# sources/test-tools/syzkaller/pkg/ast/clone.go

## Purpose
Implements deep-copy behavior for every AST node type.

## Important APIs, Types, and Functions
`(*Description).Clone` and each node's `Clone` method return independent copies. Helpers `cloneFields`, `cloneInts`, `cloneTypes`, and `cloneComments` clone slices.

## Control Flow
Each method copies scalar fields and recursively clones child nodes. Optional fields such as call return type, typedef type/struct, and binary expressions are nil-checked.

## State and Persistence Behavior
Creates in-memory copies only. Clone preserves source positions, comments, formatting choices, and AST shape.

## Dependencies and Integration Points
Used by `Filter`, tests, and callers that need to transform ASTs without mutating originals.

## Risks and Test Signals
Risks include shallow-copy bugs for slices or missing new node fields. `TestParseAll` asserts formatting of cloned descriptions matches original data.
