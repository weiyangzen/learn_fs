# sources/test-tools/strace/src/linux/x32/ioctls_arch1.h

## Purpose
Routes x32 personality 1 architecture-specific ioctl decoding to the i386 generated ioctl table.

## Important APIs, Types, and Functions
Includes `../i386/ioctls_arch0.h`, which supplies x86 arch-specific ioctl rows with 32-bit encoded sizes for the i386 personality.

## Control Flow and Integration
Compile-time inclusion populates the secondary ioctl table used when tracing 32-bit i386 processes from an x32 build.

## State and Persistence
No local state; contributes static metadata through the include.

## Dependencies
Depends on the i386 generated ioctl table and correct personality selection.

## Risks
Using this table for native x32 would decode size-sensitive ioctls incorrectly; it must remain tied to personality 1 only.

## Test Signals
Trace i386-personality ioctl calls under x32 strace and verify request names and encoded sizes match i386, especially KVM and x86 arch-specific commands.
