# sources/storage-engines/wiredtiger/src/support/update_vector.c Research

## Purpose
This file implements `WT_UPDATE_VECTOR`, a small stack-first vector of `WT_UPDATE *` pointers. It is optimized for the common case where only a small number of updates are collected, avoiding heap allocation until the embedded stack buffer is exhausted.

## Important APIs, Types, and Functions
- `__wt_update_vector_init` zeroes the structure, records the owning session, and points `listp` at the embedded `list` array.
- `__wt_update_vector_push` appends one update pointer, migrating from stack storage to heap storage via `__wt_realloc_def` when `size >= WT_UPDATE_VECTOR_STACK_SIZE`.
- `__wt_update_vector_pop` and `__wt_update_vector_peek` return the last update pointer and assert the vector is non-empty.
- `__wt_update_vector_clear` resets logical size without freeing heap storage.
- `__wt_update_vector_free` frees heap storage if it exists and reinitializes the vector.

## Control Flow and State
The vector starts with `allocated_bytes == 0` and `listp == list`. On the first push beyond stack capacity, it temporarily sets `listp = NULL`, reallocates enough heap capacity for `size + 1`, and copies the embedded stack array to the heap. Later growth uses realloc in place. If migration allocation fails, the error path restores `listp` to the stack buffer and clears `allocated_bytes`, preserving the pre-call vector contents.

## State and Persistence Behavior
The vector owns only pointer-array storage, not the pointed-to `WT_UPDATE` objects. Clearing or freeing the vector does not free updates. Persistence behavior is indirect: callers use the collected update pointers during transaction, reconciliation, or visibility algorithms, and this helper's job is to preserve collection order and memory safety.

## Dependencies and Integration Points
The file depends on WiredTiger allocation helpers, assertion macros, `WT_UPDATE`, and `WT_UPDATE_VECTOR_STACK_SIZE`. It is a reusable support container and has no direct storage-engine policy.

## Risks and Edge Cases
The critical edge case is migration failure from stack to heap; the code explicitly restores the original stack-backed state. Pop and peek are assertion-protected rather than error-returning, so callers must guarantee non-empty state. Because `clear` keeps heap memory, long-lived vectors that temporarily grow large retain that allocation until `free` is called. The vector is not synchronized and must remain session-local or externally protected.

## Test Signals
Unit tests should push exactly stack capacity, stack capacity plus one, and many more elements; verify order through peek/pop; inject allocation failure during first heap migration; verify `clear` preserves reusable heap capacity; and verify `free` returns the vector to stack-backed initialized state.
