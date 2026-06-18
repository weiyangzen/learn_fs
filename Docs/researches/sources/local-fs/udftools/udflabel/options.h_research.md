# File Research: sources/local-fs/udftools/udflabel/options.h

## Role

Parser declaration and option token definitions for `udflabel`.

## Contents

- Forward-declares `struct udf_disc`.
- Declares the long `parse_args()` signature that fills update buffers and force flag.
- Defines no-argument tokens for help, charset options, force, and no-write.
- Defines required-argument tokens for block/VAT/start/last controls and all identifier fields.

## Research Notes

This header’s large parser signature mirrors `udflabel/main.c`’s update buffer set. Any new label field requires coordinated changes here, `options.c`, and `main.c`.
