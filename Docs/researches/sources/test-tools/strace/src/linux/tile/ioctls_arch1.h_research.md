# sources/test-tools/strace/src/linux/tile/ioctls_arch1.h

## Purpose
Placeholder/generated architecture-specific ioctl table for Tile personality 1.

## Important APIs, Types, and Functions
Contains only the `ioctls_gen.sh` provenance comment and no ioctl initializer rows.

## Control Flow and Integration
Included for the secondary Tile personality ioctl table. Actual decoding relies on generic/compat ioctl include files rather than local architecture-specific rows.

## State and Persistence
No runtime or table state is introduced.

## Dependencies
Depends on ioctl table generation and the personality-specific include layout.

## Risks
Compat-specific Tile ioctl constants are absent unless the generator later adds rows. Since this file is intentionally empty, regressions are more likely in include ordering than in logic.

## Test Signals
Build the secondary Tile personality ioctl table and confirm generic 32-bit ioctl entries are still available through `ioctls_inc1.h`.
