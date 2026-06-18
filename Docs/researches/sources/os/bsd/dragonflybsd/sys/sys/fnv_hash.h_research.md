# File Research: sources/os/bsd/dragonflybsd/sys/sys/fnv_hash.h

`fnv_hash.h` implements a 32-bit Fowler/Noll/Vo hash helper. It defines `Fnv32_t`, `FNV1_32_INIT`, and `FNV_32_PRIME`.

The active inline function is `fnv_32_buf()`, which hashes a byte buffer by multiplying by the FNV prime and XORing each byte. A string variant is present but disabled under `#if 0`.

This is a lightweight public-domain utility header for non-cryptographic hashing.
