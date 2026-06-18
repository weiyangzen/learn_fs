# File Research: sources/local-fs/reiserfsprogs/include/swab.h

Endian conversion compatibility header. It defines constant and runtime byte-swap helpers for 16/32/64-bit values and supplies `cpu_to_le*`, `le*_to_cpu`, and constant variants when system headers have not already defined them. Little-endian builds use casts; big-endian builds use byte swapping. Non little/big endian architectures are rejected.
