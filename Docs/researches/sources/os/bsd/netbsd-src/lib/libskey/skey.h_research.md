# File Research: sources/os/bsd/netbsd-src/lib/libskey/skey.h

## Purpose
Defines the public S/Key API, state structures, and size limits.

## Main Interfaces
Defines `struct skey` for server-side keyfile scanning and `struct mc` for client-side challenge scanning. Declares APIs for challenge lookup, verification, key generation/format conversion, password reading, authentication, algorithm selection, key iteration, and key disabling.

## Key Constants
Defines maximum sequence number, password length bounds, seed length, challenge length, hash-name length, binary key size, and the bogus-challenge random-file path.

## Dependencies
Includes `<stdio.h>` for `FILE *`.

## Risks And Notes
`struct skey` stores pointers into its internal `buf`, so callers must not expect `logname`, `seed`, or `val` to remain valid after another scan overwrites the buffer. Several APIs use static or caller-provided buffers rather than allocated ownership.
