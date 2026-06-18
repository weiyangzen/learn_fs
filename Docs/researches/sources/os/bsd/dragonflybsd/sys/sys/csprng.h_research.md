# File Research: sources/os/bsd/dragonflybsd/sys/sys/csprng.h

Kernel CSPRNG state and API header based on SHA-256 pools and ChaCha stream cipher state.

Key responsibilities:
- Defines call flags for try-lock behavior and unlimited `/dev/urandom` reads.
- Defines `struct csprng_pool` with byte count and SHA-256 context.
- Defines cache-aligned `struct csprng_state` with key, reseed count, ChaCha context, 32 entropy pools, per-source pool index table, spinlock, reseed callout, failed reseed counter, entropy source counters, last reseed time, and IBAA/L15 state.
- Declares initialization, random output, and entropy injection functions.
- Asserts SHA-256 digest length is 32 bytes.

Dependencies:
- Includes ChaCha, SHA-2, callout, spinlock, time, and `ibaa` headers.
- Uses `__cachealign` and `CTASSERT`.

Notable risks:
- State has fixed 256 source IDs and 32 pools.
- Correct locking and reseed scheduling are critical for entropy safety and avoiding blocking/read-path races.
