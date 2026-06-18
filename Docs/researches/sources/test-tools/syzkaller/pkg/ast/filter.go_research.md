# sources/test-tools/syzkaller/pkg/ast/filter.go

## Purpose
Provides top-level AST filtering while preserving deep-copy isolation.

## Important APIs, Types, and Functions
`(*Description).Filter(predicate func(Node) bool) *Description` returns a new description containing clones of nodes for which the predicate returns true.

## Control Flow
Iterates only top-level nodes, applies predicate, clones accepted nodes, and appends them to the result.

## State and Persistence Behavior
No mutation of the original description. Output is in-memory only.

## Dependencies and Integration Points
Depends on node `Clone` implementations. Used by AST consumers selecting subsets of declarations.

## Risks and Test Signals
Filtering is non-recursive, which callers must understand. Parser tests verify all-true and all-false behavior.
