# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscolor1.h

## Purpose
Public client interface for Level 1 extended color facilities.

## Key Contents
- Declares CMYK current/set routines.
- Declares black generation and undercolor removal setters, remap variants, and current accessors.
- Declares color transfer setter, remap variant, and current accessor.

## Dependencies
Requires the base color interface context, especially `gs_mapping_proc`.

## Research Notes
Implementation is primarily in `gscolor1.c`, with current CMYK retrieval implemented elsewhere in the Ghostscript library.
