# File Research: sources/os/bsd/netbsd-src/lib/libc/db/hash/hash_log2.c

Defines `__log2`, a helper returning the number of bits needed to cover a positive integer rounded up to a power-of-two bucket/segment size. It returns zero for input zero, decrements the input, then grows a `2^i - 1` limit until the limit covers the decremented value.

Dependencies: used by hash initialization, bucket-size rounding, segment sizing, spare split point calculations, and bucket-to-page address translation.

Risks/invariants: despite its name, the function computes a ceiling-style exponent used for sizing, not the mathematical floor log2 for all inputs.
