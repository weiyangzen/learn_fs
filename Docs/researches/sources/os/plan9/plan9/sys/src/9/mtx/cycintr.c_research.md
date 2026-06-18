# File Research: sources/os/plan9/plan9/sys/src/9/mtx/cycintr.c

## Role

Stub timer scheduling hooks for the MTX port. It declares that no cycle timer is available and leaves timer add/delete/scheduler interrupt functions empty.

This is timing infrastructure placeholder code, not filesystem code.

## Main Interfaces

- `havetimer()`
- `timeradd(Timer *)`
- `timerdel(Timer *)`
- `clockintrsched()`

## Important Behavior

- `havetimer` returns `0`.
- The other functions are no-ops.

## Dependencies And Assumptions

- Included to satisfy shared kernel timer interfaces.
- Assumes the MTX port does not use the generic cycle-timer queue here.

## Notable Risks

- Any subsystem expecting high-resolution timer support will not get it from this file.
