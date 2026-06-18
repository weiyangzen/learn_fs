# File Research: sources/os/bsd/netbsd-src/sys/sys/wchan.h

Read completely: 37 lines.

Defines `wchan_t` as `volatile const void *`, the typed wait-channel identifier used by sleep/wakeup-style kernel synchronization interfaces.

Risks and notes:
- The volatile-qualified opaque pointer expresses identity only; callers should not dereference wait channels.
