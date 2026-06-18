# sources/security-integrity/selinux/libsepol/cil/src/cil_stack.c

## Purpose

`cil_stack.c` implements a small growable stack used by CIL traversals and cycle checks. It stores pairs of `enum cil_flavor` and opaque data pointers.

## Important APIs, Types, and Functions

`cil_stack_init()` allocates a stack with initial capacity 16 and `pos = -1`. `cil_stack_destroy()` frees the backing array and stack object. `cil_stack_empty()`, `cil_stack_is_empty()`, and `cil_stack_number_of_items()` query or clear state. `cil_stack_push()` grows capacity by doubling with `cil_realloc()` and writes the next `cil_stack_item`. `cil_stack_pop()`, `cil_stack_peek()`, and `cil_stack_peek_at()` expose items by stack position.

## Control Flow

Push increments `pos` first, then resizes if the new position equals capacity. Pop returns `NULL` for an empty stack, otherwise decrements `pos` and returns a pointer to the previous top slot. `peek_at(stack, pos)` treats `pos` as an offset down from the current top.

## State and Persistence Behavior

The stack owns only its dynamic backing array, not `item.data`. Returned item pointers point into the internal array and remain valid only until the stack is mutated or destroyed.

## Dependencies and Integration Points

The implementation uses `cil_malloc()` and `cil_realloc()` from `cil_mem.h`. It is used by resolver inheritance-loop checks and verifier self-reference checks, through direct calls and the iteration macros from `cil_stack.h`.

## Risks and Test Signals

The API does not guard against `NULL` stack arguments except in destroy. Consumers must not retain returned item addresses across push operations that may reallocate. Tests should cover empty pop/peek, capacity growth beyond 16, `peek_at()` bounds, and iteration order expected by cycle detection.
