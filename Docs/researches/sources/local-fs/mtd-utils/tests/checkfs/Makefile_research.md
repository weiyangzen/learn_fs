# File Research: sources/local-fs/mtd-utils/tests/checkfs/Makefile

## Purpose
Build file for the `checkfs` power-fail filesystem test utilities.

## Key Elements
Defines targets `checkfs` and `makefiles`, includes `../../common.mk`, and links both targets with the shared `comm.o` object from the build directory.

## Dependencies
Depends on the mtd-utils common make rules and `comm.c`.

## Behavior/Risks
Both binaries get the serial/power-control communication object even though `makefiles` only initializes test files.
