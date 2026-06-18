# sources/test-tools/strace/src/linux/tile/ioctls_inc1.h

## Purpose
Routes Tile personality 1 ioctl decoding to the generic 32-bit ioctl include table.

## Important APIs, Types, and Functions
The file contains `#include "../32/ioctls_inc.h"` and defines no local rows or functions.

## Control Flow and Integration
Compile-time inclusion fills the secondary Tile ioctl table with compat 32-bit ioctl metadata.

## State and Persistence
No local state. The compiled table metadata is static.

## Dependencies
Depends on `../32/ioctls_inc.h`, whose internal alignment choices depend on architecture macros and structure sizes.

## Risks
Compat ioctl sizes are pointer-width and alignment sensitive. Wrong routing would break decoding for TileGx32 or TILEPro processes.

## Test Signals
Run compat Tile ioctl traces and verify size-sensitive ioctls decode with 32-bit layouts.
