# File Research: sources/local-fs/udftools/udfinfo/options.h

## Role

Parser declaration and option token definitions for `udfinfo`.

## Contents

- Forward-declares `struct udf_disc`.
- Declares `parse_args(int, char *[], struct udf_disc *, char **)`.
- Defines no-argument tokens for help and charset switches.
- Defines required-argument tokens for block size, VAT block, start block, and last block.

## Research Notes

Small, local API header for `udfinfo/options.c`.
