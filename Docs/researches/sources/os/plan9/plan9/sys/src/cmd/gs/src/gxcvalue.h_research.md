# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcvalue.h

## Purpose
Defines the driver-interface type and conversion macros for device gray/RGB/colorant component values.

## Public Surface
- `gx_color_value`: unsigned short component value type.
- `gx_color_value_bits`, `gx_max_color_value`: component precision and maximum.
- Byte conversion macros: `gx_color_value_to_byte`, `gx_color_value_from_byte`.
- Fraction conversion macros: `frac2cv`, `cv2frac`.

## Semantics
- Component precision is tied to `sizeof(unsigned short)`, typically 16 bits.
- Byte expansion repeats high bits into low bits so 8-bit values scale across the full component range.

## Dependencies
Requires architecture size macros and fraction conversion macros from included Ghostscript base headers.

## Risks and Notes
- The comment says supported component precision must be between 8 and 16 bits; code assumes that range.

Filesystem relevance: none. This is a color component type definition.
