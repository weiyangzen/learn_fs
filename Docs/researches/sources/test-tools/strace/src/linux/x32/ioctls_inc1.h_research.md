# sources/test-tools/strace/src/linux/x32/ioctls_inc1.h

## Purpose
Connects x32's secondary ioctl table to the i386 ioctl definitions by including `../i386/ioctls_inc0.h`.

## Important APIs, Types, And Data
This is a one-line include fragment, not an API provider by itself. Its effective data is the 32-bit ioctl initializer table from the i386 directory. The including code receives the same initializer row format used by other `ioctls_inc*.h` files.

## Control Flow
No runtime control flow exists. During preprocessing, the i386 ioctl table is substituted wherever the x32 `ioctls_inc1.h` fragment is included. This lets multi-personality x86 builds keep separate ioctl tables while sharing the 32-bit ABI catalogue.

## State And Persistence
No mutable state or persistence. The file persists an architecture relationship: x32 personality slot 1 reuses the i386 ioctl table rather than duplicating generated data.

## Dependencies And Integration Points
Depends directly on `sources/test-tools/strace/src/linux/i386/ioctls_inc0.h`, which itself includes the generic 32-bit ioctl table. It integrates with the same ioctl sorting and lookup generation path as `ioctls_inc0.h`; the important behavior is determined by the included i386 fragment.

## Risks
The risk is include-target drift. If personality numbering or 32-bit ioctl table layout changes, this alias could silently point x32's companion table at the wrong ABI. Because the file has no local guard or validation, build and generated-output comparisons are the main protection.

## Test Signals
Build preprocessing should resolve the include without duplicate-definition problems. Ioctl lookup tests should confirm that x32 builds can decode both x32-native and i386-personality ioctl request numbers. Regeneration should preserve this include if the table-sharing relationship remains valid.

## Source-Read Signal
Reviewed the complete local file; it consists solely of `#include "../i386/ioctls_inc0.h"`.
