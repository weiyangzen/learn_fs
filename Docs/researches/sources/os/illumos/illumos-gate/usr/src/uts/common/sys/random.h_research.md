# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/random.h

## Role

`random.h` defines random-device and software-random-provider statistics, kernel entropy/random-byte entry points, and the `getrandom(2)` user ABI flags.

## Statistics

`rnd_stats_t` counts bytes generated for `/dev/random`, bytes read from the random cache, and bytes generated for `/dev/urandom`.

`swrand_stats_t` tracks entropy estimate, entropy in/out, and raw bytes in/out for the kernel random provider.

Kernel/stat macros update per-CPU or global stats through direct increments or atomics.

## Interfaces

Kernel or fake-kernel builds declare:
- `random_add_entropy()`
- `random_get_bytes()`
- `random_get_blocking_bytes()`
- `random_get_pseudo_bytes()`

Userland sees `getrandom(void *, size_t, unsigned int)` and flags:
- `GRND_NONBLOCK`
- `GRND_RANDOM`

## Research Notes

This is the public and kernel-facing random API header. The distinction between blocking, pseudo, and `/dev/random`-selected behavior is the main semantic surface.
