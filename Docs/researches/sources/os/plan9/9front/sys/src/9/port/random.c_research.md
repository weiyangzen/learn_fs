# File Research: sources/os/plan9/9front/sys/src/9/port/random.c

Kernel random generator seeded from hardware RNG and timer jitter, backed by ChaCha.

Key responsibilities:
- Exposes optional machine-specific `hwrandbuf`.
- Starts a `randomseed` kernel process in `randominit()`.
- Collects seed bytes using a periodic timer with a frequency close to but not equal to HZ and a busy-loop counter.
- Mixes the seed with SHA2-512 and initializes a 20-round ChaCha state.
- Implements `randomread()` by optionally filling with hardware random, copying/rekeying ChaCha state, incrementing IV/counter, and encrypting the caller buffer.
- Provides `genrandom()` wrapper and `lrand()` using xoroshiro128+ seeded from `randomread()`.

Important behavior:
- `randominit()` locks the ChaCha state until `randomseed()` completes; reads block on that qlock.
- `randomread()` zeros the local copied ChaCha state after use.
- `lrand()` seeds only once and retries until the state is nonzero.

Notable risks:
- Entropy collection is timing-dependent if no hardware RNG exists.
- `randomread()` encrypts directly into caller memory, which may fault after state has been copied/rekeyed.
