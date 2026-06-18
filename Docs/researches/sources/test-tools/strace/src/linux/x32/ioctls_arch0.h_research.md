# sources/test-tools/strace/src/linux/x32/ioctls_arch0.h

## Purpose
Routes x32 personality 0 architecture-specific ioctl decoding to the x86_64 generated ioctl table.

## Important APIs, Types, and Functions
Includes `../x86_64/ioctls_arch0.h`, which contains x86 architecture ioctl rows such as machine-check, MSR, MTRR, SGX, and KVM request metadata with 64-bit-oriented sizes.

## Control Flow and Integration
Compile-time inclusion contributes x86_64 arch-specific ioctl rows before generic include rows in the ioctl decoder.

## State and Persistence
No local state. The included rows become static ioctl metadata.

## Dependencies
Depends on x86_64 generated ioctl table and x32 ioctl ABI compatibility for native x32 processes.

## Risks
x32 ioctl sizes can differ from both pure 32-bit and 64-bit ABIs. Reusing x86_64 rows is correct only for commands whose kernel-facing structure sizes match x32 expectations.

## Test Signals
x32 ioctl tests should cover x86-specific commands, especially KVM and MSR/MTRR requests with encoded sizes.
