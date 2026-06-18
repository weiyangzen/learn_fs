# sources/test-tools/strace/src/linux/tile/ioctls_inc0.h

## Purpose
Routes Tile personality 0 ioctl decoding to the generic 64-bit ioctl include table.

## Important APIs, Types, and Functions
The file contains `#include "../64/ioctls_inc.h"` and exports no local symbols.

## Control Flow and Integration
Compile-time inclusion populates personality 0's ioctl table with 64-bit generic ioctl definitions after any architecture-specific rows.

## State and Persistence
No local mutable state; the include contributes static ioctl metadata to the compiled decoder.

## Dependencies
Depends on `../64/ioctls_inc.h` and the ioctl table assembly context.

## Risks
Using the wrong generic include would produce incorrect ioctl sizes for pointer-width-sensitive commands. This file must stay aligned with Tile native word size.

## Test Signals
Trace common ioctls on native Tile and verify decoded request names and structure sizes match 64-bit ABI expectations.
