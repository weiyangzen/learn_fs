# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_component.h

## Summary
Public declarations for rumpuser component helper functions.

## Key Details
- Declares schedule/unschedule wrappers.
- Declares host-error translation.
- Declares component kernel-thread and LWP helper functions.
- Uses an include guard for `_RUMP_RUMPUSER_COMPONENT_H_`.

## Notes
The header references `struct lwp` without defining it, expecting consumers to share the rump kernel type context.
