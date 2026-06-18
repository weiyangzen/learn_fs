# sources/user-network-fs/nfs-ganesha/src/include/os/acl.h

## Purpose
This is the OS-neutral include point for non-standard POSIX ACL APIs. It hides platform-specific ACL headers behind one `os/acl.h` path.

## Important APIs, Types, And Functions
The header includes `config.h` and, when `LINUX` is defined, includes `<os/linux/acl.h>`. It declares no functions or types itself.

## Control Flow
All behavior is compile-time conditional inclusion. Linux builds receive the Linux ACL shim; non-Linux builds currently receive only the guard and config include.

## State And Persistence
There is no runtime state or persistence. The file controls preprocessor visibility of platform ACL declarations.

## Dependencies And Integration Points
It depends on build configuration macros from `config.h`. FSAL and permission code can include this common path without directly selecting Linux ACL headers.

## Risks And Test Signals
Risks include silent absence of ACL declarations on platforms that need their own shim and accidental build macro mismatch. Test signals are compile tests for Linux and non-Linux configurations, plus ACL feature tests in FSAL modules that include `os/acl.h`.
