# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_error.cpp

## Purpose
Tests error-preservation and error-priority behavior for `WT_TRET` and `WT_TRET_ERROR_OK`.

## Important APIs, Types, And Functions
Uses `WT_DECL_RET`, `WT_TRET`, and `WT_TRET_ERROR_OK` with WiredTiger error codes including `WT_PANIC`, `WT_RUN_RECOVERY`, `WT_ERROR`, `WT_DUPLICATE_KEY`, `WT_NOTFOUND`, `WT_RESTART`, and `WT_CACHE_FULL`.

## Control Flow
Sections initialize `ret` to different values, invoke the macro with a new status, and assert the resulting priority. `WT_TRET_ERROR_OK` additionally treats a configured acceptable error as success.

## State And Persistence Behavior
Only a local `ret` variable is mutated. No persistence or connection state is involved.

## Dependencies And Integration Points
Depends on Catch2, `wiredtiger.h`, and `wt_internal.h`. It validates common cleanup/error-chaining macros used throughout WiredTiger.

## Risks And Edge Cases
Risks include panic/recovery priority being overwritten incorrectly, benign errors not being suppressed by `WT_TRET_ERROR_OK`, or special statuses behaving like generic errors.

## Test Signals
The final `ret` value in each section must match the macro's intended priority rules.
