# sources/user-network-fs/nfs-ganesha/src/include/os/freebsd/extended_types.h

## Purpose
This FreeBSD extended-types shim centralizes platform type includes for code that expects OS-specific type completion.

## Important APIs, Types, And Functions
It includes `<sys/types.h>` and declares no new aliases, structs, or functions.

## Control Flow
The header is compile-time only. Including it makes standard FreeBSD system types available through a Ganesha OS abstraction path.

## State And Persistence
There is no runtime state or persistent behavior.

## Dependencies And Integration Points
It depends on FreeBSD system headers and integrates with code that includes `os/<platform>/extended_types.h` for platform-specific type availability.

## Risks And Test Signals
Risks are minimal but include missing future FreeBSD-specific aliases if generic code starts requiring them. Test signals are FreeBSD compile coverage for FSAL and utility files that include extended types.
