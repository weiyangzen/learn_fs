# sources/test-tools/fio/err.h

## Purpose
`err.h` provides Linux-kernel-style pointer/error helpers for returning either a valid pointer or a small negative errno encoded in a pointer-sized value.

## Important APIs, Types, And Functions
`MAX_ERRNO` is `4095`, matching the conventional maximum errno range. `IS_ERR_VALUE(x)` tests whether an unsigned pointer-sized value falls in the high address range reserved for encoded negative errors. `ERR_PTR(error)` casts an integer error to `void *`. `PTR_ERR(ptr)` casts a pointer back to an integer. `IS_ERR(ptr)` and `IS_ERR_OR_NULL(ptr)` test encoded error pointers, and `PTR_ERR_OR_ZERO(ptr)` returns the encoded error or zero.

## Control Flow
The header is all inline/macro logic. Callers create an encoded error with `ERR_PTR(-EINVAL)`-style values, propagate it through pointer-returning APIs, then test with `IS_ERR` before dereferencing.

## State And Persistence
No state is stored. Behavior depends entirely on pointer representation and the assumption that valid pointers do not occupy the reserved top `MAX_ERRNO` range.

## Dependencies And Integration Points
The code uses `uintptr_t`; including translation units must already have the needed integer type definitions. It integrates with fio code that mirrors Linux kernel pointer-error idioms.

## Risks
This pattern is architecture-sensitive. It is safe only if callers consistently pass negative errno values and never dereference before checking. `PTR_ERR_OR_ZERO()` returns `int` but `PTR_ERR()` returns `uintptr_t`; callers should avoid losing information or sign semantics accidentally.

## Test Signals
Simple unit tests can check that `ERR_PTR((uintptr_t)-EINVAL)` is detected, NULL is handled by `IS_ERR_OR_NULL`, normal heap pointers are not errors, and `PTR_ERR_OR_ZERO()` returns zero for normal pointers.
