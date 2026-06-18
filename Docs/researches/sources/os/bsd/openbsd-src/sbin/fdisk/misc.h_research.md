# File Research: sources/os/bsd/openbsd-src/sbin/fdisk/misc.h

## Purpose
Declares shared `fdisk` utility types, constants, globals, and functions.

## Key Contents
- `struct unit_type` describes display unit abbreviation, conversion factor, and long name.
- Defines `nitems()` fallback.
- Defines whitespace, trim mode, and line buffer constants.
- Exposes global `verbosity`.
- Declares unit conversion, input, yes/no prompt, hex parsing, bounded numeric prompt, and UUID parsing helpers.

## Notes
This header supports both interactive command handling and GPT/MBR display code.
