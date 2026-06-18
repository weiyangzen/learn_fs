# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sha1_consts.h

## Role

Defines SHA-1 round constants and architecture-dependent constant-loading policy.

## Key Interfaces

- Exports `sha1_consts[]`.
- On SPARC, `SHA1_CONST(x)` loads from `sha1_consts[x]`.
- On other architectures, `SHA1_CONST(x)` expands to immediate `SHA1_CONST_<x>`.
- Defines FIPS 180-1 constants `SHA1_CONST_0` through `SHA1_CONST_3`.

## Rationale

SPARC loads 32-bit constants more cheaply from memory than from synthesized immediates, while Intel and other processors generally benefit from direct constants.

## Risk Notes

The macro must match implementation expectations in `SHA1Transform()`. Constant values are algorithm-defined and must not change.
