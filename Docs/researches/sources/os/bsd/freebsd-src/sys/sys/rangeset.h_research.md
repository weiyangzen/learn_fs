# File Research: sources/os/bsd/freebsd-src/sys/sys/rangeset.h

Read completely: 94 lines.

## Purpose
Declares the kernel rangeset API for maintaining non-overlapping or managed integer ranges with caller-embedded elements.

## Main Elements
- Includes private `_rangeset` definitions under `_KERNEL`.
- Defines predicate callback type `rs_pred_t`.
- Defines `struct rs_el`, which must be embedded at the start of application data and stores start/end range keys.
- Declares init/fini, empty checks, insert, remove all, remove by range, remove by predicate, containing lookup, range-empty query, beginning lookup, and copy operations.
- Documents that remove may need to split elements and can fail with `ENOMEM` without modifying the set.
- Documents copy failure leaves destination empty.

## Dependencies And Integration
Used by kernel range-tracking subsystems and backed by the private rangeset implementation, including pctrie-style start keys and caller-provided duplication/free callbacks.

## Risk Notes
Caller data layout must start with `struct rs_el`. Removal and copy have transactional guarantees that implementation and callbacks must preserve.
