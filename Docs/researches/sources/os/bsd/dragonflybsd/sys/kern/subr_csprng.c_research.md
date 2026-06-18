# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_csprng.c

Fortuna-like CSPRNG state machine built from SHA-256 entropy pools and embedded ChaCha20 keystream generation.

Key responsibilities:
- Initializes 32 SHA-256 entropy pools, the ChaCha key/context, source-to-pool round-robin indexes, reseed counters, and timestamps.
- Adds entropy by hashing source ID, byte count, and entropy bytes into a rotating pool selected per 8-bit source ID.
- Reseeds from pool 0 only after a minimum pool byte threshold, and folds higher-numbered pools in on reseed counts divisible by powers of two.
- Updates the ChaCha key from SHA-256(old key || selected pool digests), resets the 128-bit counter, and generates output in bounded chunks.
- Rekeys after each output chunk by encrypting new key material from the existing stream.

Important behavior:
- Callers are expected to hold `state->spin` for both entropy addition and random generation.
- Non-`CSPRNG_UNLIMITED` consumers sleep until at least one reseed has succeeded.
- Output is limited to `2^20` bytes between rekeys.
- Callout-based reseeding code is present but disabled with `#if 0`.

Dependencies:
- Embeds `crypto/chacha20/chacha.c` with keystream-only settings and uses SHA-256 from `crypto/sha2`.
- Uses DragonFly spin locks, `ratecheck()`, `ssleep()`, and `wakeup()` conventions.

Notable risks:
- `CSPRNG_UNLIMITED` callers can receive output even before the first successful reseed, relying on that mode's weaker semantics.
- Entropy accounting is byte-count based; it does not estimate entropy quality.
- Pool byte counters grow monotonically after pool reinitialization with a digest seed, so they are not a strict measure of fresh entropy.
