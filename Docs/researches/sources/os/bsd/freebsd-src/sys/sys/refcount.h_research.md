# File Research: sources/os/bsd/freebsd-src/sys/sys/refcount.h

Read completely: 220 lines.

## Purpose
Provides atomic unsigned reference count helpers with saturation protection and acquire/release memory ordering.

## Main Elements
- Defines saturated refcount detection and saturation value.
- On overflow/underflow, panics under `INVARIANTS` or stores saturation to prefer leaks over premature object destruction.
- Provides initialization, load, acquire, acquire-n, checked acquire, acquire-if-greater-than, and acquire-if-not-zero helpers.
- Provides release-n/release helpers with release fence before decrement and acquire fence on last reference.
- Defines conditional release helper generators for greater-than and equal-to cases.
- Provides public conditional release helpers for `release_if_gt`, `release_if_last`, and `release_if_not_last`.

## Dependencies And Integration
Used throughout kernel lifetime management. Depends on machine atomic operations, kassert/panic behavior, and C bool support outside kernel/standalone.

## Risk Notes
Correct destructor visibility depends on the release/acquire fences. Saturation avoids use-after-free on wraparound but can leak objects; callers must check result-use annotations where required.
