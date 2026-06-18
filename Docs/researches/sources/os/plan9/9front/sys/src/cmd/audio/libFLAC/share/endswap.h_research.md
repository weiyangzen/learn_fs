# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/share/endswap.h

## Role

`share/endswap.h` defines endian byte-swap macros and host-to-little-endian conversions used by FLAC internals.

## Contents

It selects `ENDSWAP_16`, `ENDSWAP_32`, and `ENDSWAP_64` from compiler builtins, MSVC `_byteswap_*`, Linux `<byteswap.h>`, or portable bit-shift fallbacks. It also defines `H2LE_16` and `H2LE_32` for MD5 sample formatting, swapping only on big-endian CPUs.

## Risks / Edge Cases

- `CPU_IS_BIG_ENDIAN` must be defined accurately by configuration for `H2LE_*`.
- The portable `ENDSWAP_64` macro composes 32-bit swaps and assumes unsigned-style shift behavior on supplied values.
- This header assumes `config.h` has already supplied feature macros.

## Dependencies

May use compiler builtins, `<stdlib.h>`, or `<byteswap.h>` depending on platform macros.
