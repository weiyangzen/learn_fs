# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/edonr.h

This header declares the Edon-R hash implementation interface and state layout, adapted from a NIST/SUPERCOP-style implementation.

Key contents:
- Digest and block sizes for EdonR-224, EdonR-256, EdonR-384, and EdonR-512.
- Block bit sizes for 256-bit and 512-bit variants.
- Internal state structs:
  - `EdonRData256`
  - `EdonRData512`
  - `EdonRState`
- Public hash API:
  - `EdonRInit`
  - `EdonRUpdate`
  - `EdonRFinal`
  - `EdonRHash`

Dependencies:
- Includes `sys/types.h`.
- Uses fixed-width integer types and `size_t`.
- Uses C++ guards.

Research notes:
- The comment warns that consecutive `EdonRUpdate()` calls are constrained by the amount of unprocessed plus newly supplied data relative to the compression block size; otherwise an assertion failure is invoked.
- Filesystem relevance is likely through checksum/hash consumers, especially storage code that can use Edon-R as an algorithm primitive.
