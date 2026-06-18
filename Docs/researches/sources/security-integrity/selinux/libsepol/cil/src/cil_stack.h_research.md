# sources/security-integrity/selinux/libsepol/cil/src/cil_stack.h

## Purpose

`cil_stack.h` defines the stack container and iteration macros used by resolver and verifier recursion checks.

## Important APIs, Types, and Functions

`struct cil_stack` contains the backing `stack` array, capacity `size`, and top index `pos`. `struct cil_stack_item` stores a CIL flavor tag plus opaque `data`. The macros `cil_stack_for_each_starting_at()` and `cil_stack_for_each()` iterate from the top downward through `cil_stack_peek_at()`. Function prototypes cover initialization, destruction, emptying, item counting, push, pop, peek, and indexed peek.

## Control Flow and Integration

The iteration macros are designed for stack-based ancestor checks, where offset zero is the current top. They are used by resolver inheritance checks and verifier self-reference checks to scan active recursion frames.

## State, Dependencies, and Risks

The header depends on `enum cil_flavor` being visible through prior includes in consumers. It does not enforce ownership for `data`; callers supply and retain pointee lifetimes. Macro arguments are evaluated multiple times in the `for` expansion through `cil_stack_peek_at()`, so callers should pass simple variables.

## Test Signals

Compile tests should include the header after the usual CIL internal headers. Runtime tests should verify macro traversal order and behavior when starting offsets are beyond stack depth.
