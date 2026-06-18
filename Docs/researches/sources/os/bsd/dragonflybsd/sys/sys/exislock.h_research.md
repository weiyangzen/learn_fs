# File Research: sources/os/bsd/dragonflybsd/sys/sys/exislock.h

`exislock.h` documents and declares DragonFly's existential lock state. The long file comment explains the design: readers enter type-safe critical sections with `exis_hold()`/`exis_drop()` while object owners can unlink, cache, terminate, poll, and eventually reuse/free structures after pseudo-tick grace periods.

The header defines `struct exislock` containing a `pseudo_ticks` deadline/state value, `exislock_t`, and `exis_state_t` values `EXIS_TERMINATE`, `EXIS_NOTCACHED`, `EXIS_CACHED`, and `EXIS_LIVE`.

It declares the global `pseudo_ticks`. The actual inline operations live in `exislock2.h`.
