# File Research: sources/teaching/pintos/src/filesys/off_t.h

## Purpose
Defines the Pintos file-offset type in a small standalone header to avoid pulling in broader file-system declarations.

## Contents
- Includes `<stdint.h>`.
- Defines:
  - `typedef int32_t off_t`
  - `PROTd` as `PRId32` for formatted printing.

## Important Behavior
- File offsets are signed 32-bit values.
- This bounds representable file sizes and offsets to the `int32_t` range in this teaching file system.

## Research Notes
- The comment explains this header exists because multiple headers need `off_t` without needing other file-system APIs.
