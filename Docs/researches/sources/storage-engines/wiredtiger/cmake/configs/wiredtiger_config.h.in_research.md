# sources/storage-engines/wiredtiger/cmake/configs/wiredtiger_config.h.in

## Purpose
`wiredtiger_config.h.in` is the CMake template for WiredTiger's generated compile-time configuration header.

## Important APIs, Types, And Functions
It uses `#cmakedefine` for build toggles such as diagnostics, error logging, built-in extensions, call log, unit tests, memkind, Antithesis, RCpc, CRC disable, spinlock type, endian, and standalone build. It also defines POSIX feature availability by target preprocessor macros and sets `VERSION`.

## Control Flow
CMake substitutes cache variables into the template. At C compile time, platform preprocessor checks define availability for POSIX, Linux-only, x86, and ARM intrinsic features.

## State And Persistence Behavior
The generated header is a persistent build artifact under the build include directory. It directly controls compiled code paths throughout WiredTiger.

## Dependencies And Integration Points
It depends on `base.cmake` values and platform compiler macros. It is included by WiredTiger source through generated include paths and is installed indirectly through generated public headers.

## Risks
Template mistakes can silently alter broad compile-time behavior. Platform feature checks are preprocessor-based and may not capture unusual libc/kernel combinations. The `SPINLOCK_TYPE` substitution must match a valid mutex implementation macro.

## Test Signals
Configure representative Linux, macOS, NetBSD, Windows, x86_64, and aarch64 builds; inspect generated header; build with toggles for diagnostics, built-in extensions, unit tests, and RCpc.
