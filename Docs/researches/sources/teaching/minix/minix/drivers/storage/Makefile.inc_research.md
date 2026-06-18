# File Research: sources/teaching/minix/minix/drivers/storage/Makefile.inc

## Purpose
One-line make include shim for storage driver subdirectories.

## Behavior
Includes `../Makefile.inc`, inheriting shared driver build settings from the parent `drivers` tree.

## Integration Notes
Used by nested storage driver makefiles through normal BSD make include resolution.

## Risks
Any parent `Makefile.inc` change applies broadly to all storage drivers that include this file.
