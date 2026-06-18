# File Research: sources/local-fs/mtd-utils/tests/checkfs/common.h

## Purpose
Small shared header for `checkfs` and `makefiles`.

## Key Elements
Defines `TRUE`, `FALSE`, and `MAX_NUM_FILES` as `100`.

## Dependencies
None.

## Behavior/Risks
Uses un-namespaced macros and no include guard, but the header is tiny and used only by the local test programs.
