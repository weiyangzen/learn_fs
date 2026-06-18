# sources/user-network-fs/libsmb2/include/picow/config.h

## Purpose
This `config.h` snapshot configures libsmb2 for Raspberry Pi Pico W builds.

## Important APIs, Types, and Functions
It defines package metadata and selected feature macros. Most POSIX networking headers are disabled, while `HAVE_FCNTL_H`, `HAVE_DLFCN_H`, `HAVE_STDINT_H`, `HAVE_STDIO_H`, `HAVE_STDLIB_H`, `HAVE_SYS_STAT_H`, `HAVE_SYS_TYPES_H`, `HAVE_TIME_H`, `HAVE_UNISTD_H`, and `HAVE_SOCKADDR_STORAGE` are enabled.

## Control Flow
No direct control flow exists. The macros select embedded/lwIP-compatible code paths during compilation.

## State and Persistence Behavior
No runtime persistence. Compile-time feature choices affect socket/address and authentication behavior.

## Dependencies and Integration Points
It integrates with Pico SDK, lwIP, `portable-endian.h`'s `PICO_PLATFORM` path, and the Pico W FreeRTOS/lwIP option headers.

## Risks and Edge Cases
Many normal POSIX headers and string macros are disabled, so portability shims are required. Kerberos/GSSAPI is unavailable. The generated package version is `4.0.0`, which should be checked against the build/package metadata used for Pico.

## Test Signals
Cross-compile for Pico W and run DNS, TCP connect, stat/read/write, signing, and timeout behavior over lwIP.
