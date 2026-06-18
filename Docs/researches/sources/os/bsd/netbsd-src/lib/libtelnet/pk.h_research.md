# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/pk.h

## Purpose
Defines SRA public-key constants, DES/IDEA key buffers, and public-key helper prototypes.

## Main Interfaces
Defines `DesData`, `IdeaData`, DES encrypt/decrypt direction constants, fixed hex modulus, key sizes, primitive root, and prototypes for `genkeys`, `common_key`, `pk_encode`, and `pk_decode`.

## Dependencies
Depends on DES key schedule type names.

## Risks And Notes
The cryptographic parameters are fixed and small by modern standards: 192-bit public-key exchange and DES-derived session keys.
