# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysmacros.h

## Purpose
Provides common low-level macros for block/byte conversion, min/max/absolute values, device number encoding/decoding, power-of-two alignment, bitfield declaration ordering, atomic count helpers, array sizing, and saturating integer conversions.

## Main Interfaces
- Block conversion macros: `dtob()`, `btod()`, `btodt()`, `lbtod()`.
- Generic macros: `MIN`, `MAX`, `ABS`, `SIGNOF`, `__DECONST`.
- Kernel BCD conversion tables/macros:
  - `byte_to_bcd`, `bcd_to_byte`
  - `BYTE_TO_BCD()`, `BCD_TO_BYTE()`
- Device-number macros:
  - old and expanded major/minor bit constants
  - `major()`, `minor()`, `getmajor()`, `getminor()`
  - `makedev()`, `makedevice()`
  - `emajor()`, `eminor()`, `getemajor()`, `geteminor()`
  - `DEVCMPL()`, `DEVEXPL()`, `cmpdev()`, `expdev()`
- Alignment and rounding macros:
  - `IS_P2ALIGNED()`, `howmany()`, `roundup()`, `ISP2()`
  - `P2ALIGN()`, `P2PHASE()`, `P2NPHASE()`, `P2ROUNDUP()`, `P2END()`, `P2PHASEUP()`, `P2BOUNDARY()`, `P2SAMEHIGHBIT()`
  - typed variants for explicit result widths
- Count and bitfield helpers:
  - `INCR_COUNT()`, `DECR_COUNT()`
  - `DECL_BITFIELD2()` through `DECL_BITFIELD8()`
- `ARRAY_SIZE()`, `UINT64_OVERFLOW_ADD()`, and `UINT64_OVERFLOW_TO_INT64()`.

## Dependencies And Relationships
Includes `sys/param.h` and `sys/stddef.h`. It is widely included across kernel and userland headers and is especially important for device IDs and alignment-sensitive kernel code.

## Research Notes
The file warns that older major/minor macros should not be used by drivers or applications. Endianness-specific `DECL_BITFIELD*` macros require either `_BIT_FIELDS_LTOH` or `_BIT_FIELDS_HTOL`.
