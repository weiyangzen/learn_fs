# File Research: sources/os/bsd/netbsd-src/sys/sys/sha3.h

Read completely: 80 lines.

This header declares SHA-3 and SHAKE context types and APIs. The shared `struct sha3` stores the 25-lane Keccak state and remaining buffer byte count; wrapper context types are provided for SHA3-224/256/384/512 and SHAKE128/256.

APIs include init/update/final for fixed-length SHA-3 digests, variable-length finalization for SHAKE, and `SHA3_Selftest`.

Risks: no implementation here. Callers of SHAKE finalization must supply the desired output length explicitly and manage output buffers.
