# File Research: sources/os/bsd/netbsd-src/sys/sys/boot_duration.h

## Scope

Declares an optional boot-duration timer API.

## APIs

- Includes `sys/types.h`.
- If `__HAVE_BOOT_DURATION` is defined, declares `uint64_t boot_duration_timer(void)`.

## Dependencies And Role

- Used by platforms that provide a machine-specific timer suitable for measuring boot duration.

## Risks And Invariants

- Header intentionally exposes nothing on platforms without `__HAVE_BOOT_DURATION`.
