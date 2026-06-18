# File Research: sources/teaching/pintos/src/filesys/Makefile

## Purpose
One-line make wrapper for the Pintos file-system source directory.

## Contents
- Includes `../Makefile.kernel`.

## Integration Notes
- This directory relies on the shared Pintos kernel build rules rather than defining local build logic.
- File-system objects are expected to be selected through the parent kernel make infrastructure and accompanying `Make.vars`.

## Research Notes
- No local targets, compiler flags, or object lists are defined here.
