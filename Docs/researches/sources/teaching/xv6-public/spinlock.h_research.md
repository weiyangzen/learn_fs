# File Research: sources/teaching/xv6-public/spinlock.h

Defines `struct spinlock`.

Fields:
- `locked` state.
- Debug lock name.
- Owning CPU pointer.
- Saved caller program counters.

Used across nearly all shared kernel structures.
