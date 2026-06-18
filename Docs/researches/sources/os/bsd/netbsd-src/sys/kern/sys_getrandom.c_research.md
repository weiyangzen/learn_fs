# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_getrandom.c

## Purpose
Implements `getrandom(2)` and shared random-data generation logic for user buffers via `uio`.

## Main Interfaces
- `sys_getrandom`: validates `GRND_RANDOM`, `GRND_INSECURE`, and `GRND_NONBLOCK`; constructs a single-iovec `uio`; calls `dogetrandom`; returns byte count with partial-success semantics.
- `dogetrandom`: fills the supplied `uio` using fast per-CPU CPRNG or a local NIST Hash DRBG seeded from the entropy pool.

## State And Control Flow
Short non-`GRND_RANDOM` reads use `cprng_strong(user_cprng)` if entropy is ready or insecure output is allowed. Otherwise the function extracts a seed, instantiates a NIST Hash DRBG, generates output in 512-byte chunks, reseeds on DRBG interval exhaustion, and zeroes seed/buffer material before free. `/dev/random` style output is clamped to entropy capacity/seed size and stops after one buffer.

## Dependencies And Integration
Uses entropy pool APIs, CPRNG, NIST Hash DRBG, `uiomove`, signal pending checks, preemption points, and process VM-space `uio` setup.

## Risks And Edge Cases
- `GRND_RANDOM | GRND_INSECURE` is rejected as nonsensical.
- `GRND_NONBLOCK` suppresses waiting for full entropy unless insecure output is requested.
- Large requests may return partial data if reseed fails or a signal is pending after data has been transferred.
- Sensitive temporary buffers are explicitly wiped.

## Filesystem Relevance
Indirect. It is not a filesystem implementation, but its `uio` helper style overlaps with character-device random reads and generic user-buffer transfer patterns.
