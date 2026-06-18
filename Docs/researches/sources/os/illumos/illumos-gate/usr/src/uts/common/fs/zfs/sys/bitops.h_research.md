# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/bitops.h

Read status: complete, 90 lines.

Purpose: generic 32-bit and 64-bit bitfield encode/decode/get/set helpers used throughout ZFS packed metadata fields.

Key definitions:
- `BF32_DECODE`, `BF64_DECODE`, `BF32_ENCODE`, `BF64_ENCODE` implement low/length field extraction and insertion.
- `BF32_GET`, `BF64_GET`, `BF32_SET`, `BF64_SET` provide direct bitfield access with assertion checks.
- `BF32_GET_SB`, `BF64_GET_SB`, `BF32_SET_SB`, `BF64_SET_SB` add shifted-and-biased encodings for fields such as block sizes.

Important implementation constraints:
- Set macros assert value range and field bounds.
- Shift/bias variants assert power-of-two alignment and nonnegative biased value.
- The macros use `ASSERT3U`/`ASSERT3S` and `_NOTE(CONSTCOND)` to avoid lint issues.

Dependencies: `zfs_context.h`, especially `P2PHASE`, `IS_P2ALIGNED`, and assertion macros.

Research notes:
- These macros are foundational for packed fields in ARC/L2ARC, DDT keys, block pointers, and similar metadata.
