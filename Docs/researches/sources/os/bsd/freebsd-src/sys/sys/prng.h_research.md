# File Research: sources/os/bsd/freebsd-src/sys/sys/prng.h

This small public-domain header wires in the PCG pseudo-random generator variants and declares kernel PRNG helpers. It sets `PCG_USE_INLINE_ASM` before including `<contrib/pcg-c/include/pcg_variants.h>`.

Under `_KERNEL`, it declares `prng32()`, `prng32_bounded()`, `prng64()`, and `prng64_bounded()`. These provide fast non-cryptographic pseudo-random values and bounded variants for kernel consumers.

Filesystem relevance is incidental: such PRNG helpers may be used by kernel subsystems for randomized choices that do not require cryptographic randomness, but this header itself contains no filesystem-specific policy.
