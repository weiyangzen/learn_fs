# File Research: sources/os/bsd/dragonflybsd/sys/sys/uuid.h

## Summary
DCE-style UUID structure and kernel/user UUID helper declarations.

## Main Responsibilities
- Defines `struct uuid` with time, clock sequence, and six-byte node fields.
- Defines kernel `uuid_t`, comparison/classification, formatting, parsing, and endian encode/decode helpers.
- Declares userland `uuidgen()`.

## Important Behavior
The structure matches DCE 1.1 source representation rather than an opaque byte array. Kernel helpers distinguish byte-order encoding and decoding.

## Risks
Endian conversion mistakes can produce stable but wrong UUID values across disk/network formats.
