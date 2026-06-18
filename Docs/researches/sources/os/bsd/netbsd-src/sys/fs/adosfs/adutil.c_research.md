# File Research: sources/os/bsd/netbsd-src/sys/fs/adosfs/adutil.c

## Summary
Provides ADOSFS helper routines for block validation, checksums, permissions, case folding, hashing, and endian conversion.

## Main Responsibilities
- Validate AmigaDOS block checksum, primary type, and secondary type.
- Map secondary block types to `anode_type`.
- Translate AmigaDOS protection bits to Unix permission bits.
- Fold ASCII and optional international characters to uppercase for comparisons.
- Compute AmigaDOS directory hash values.
- Read big-endian words from buffers on non-big-endian systems.

## Key Interfaces
- `adosfs_getblktype()`.
- `adunixprot()`.
- `adoscksum()`.
- `adoscaseequ()`.
- `adoshash()`.
- `adoswordn()` on little-endian platforms.

## Risks
Checksum and type validation are the main guardrails against corrupt media. Permission translation has compatibility behavior for extended uid/gid bits and old protection semantics.
