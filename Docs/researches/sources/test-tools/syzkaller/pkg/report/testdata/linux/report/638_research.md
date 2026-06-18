# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/638

## Purpose
This fixture covers a KASAN use-after-free write attributed to `put_ucounts`.

## Important APIs, types, and functions
Important frames include `_atomic_dec_and_lock_irqsave`, `put_ucounts`, KASAN reporting helpers, allocation stack for the object, and free stack from another task.

## Control flow
A syzkaller executor uses an object after another task has freed it; atomic reference-count teardown attempts to write through freed memory in the ucounts path.

## State and persistence behavior
The raw log persists allocation and free stacks, task identities, object bounds, and the write classification.

## Dependencies and integration points
It tests KASAN use-after-free parsing, refcount/ucounts symbol selection, and cross-task lifetime evidence.

## Risks and test signals
The parser must not title the report as `_atomic_dec_and_lock_irqsave`; the expected semantic title is `put_ucounts` with type `KASAN-USE-AFTER-FREE-WRITE`.
