# File Research: sources/local-fs/mtd-utils/include/mtd_swab.h

## Purpose
Simple endian byte-swap and CPU/endian conversion helpers.

## Key Elements
Defines `swab16`, `swab32`, `swab64`, `cpu_to_le*`, `cpu_to_be*`, `le*_to_cpu`, and `be*_to_cpu`, selected by `__BYTE_ORDER`.

## Dependencies
Includes `endian.h` and expects fixed-width integer types to be available from callers.

## Behavior/Risks
Uses GNU statement expressions for conversion macros on swapped paths. It may conflict with system headers that already define similarly named macros.
