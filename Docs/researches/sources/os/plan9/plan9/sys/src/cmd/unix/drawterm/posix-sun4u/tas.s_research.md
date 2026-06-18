# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-sun4u/tas.s

SPARC assembly implementation of `tas`.

Behavior:
- Exports `tas`.
- Uses `ldstub [%o0], %o0` in the return delay slot.
- Returns the old byte value while atomically setting the target byte.

Role: sun4u atomic lock primitive.
