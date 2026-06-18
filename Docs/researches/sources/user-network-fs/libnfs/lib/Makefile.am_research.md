# sources/user-network-fs/libnfs/lib/Makefile.am

## Purpose
Autotools build recipe for `libnfs.la`, including source lists, include paths, version-info, and library dependencies.

## Important APIs, Types, And Functions
- `libnfs_la_CPPFLAGS` includes public and protocol directories plus `_U_` unused attribute macro.
- `libnfs_la_SOURCES` includes the same core library sources plus `../win32/win32_compat.c`.
- `libnfs_la_LDFLAGS` carries libtool version info and optional Kerberos linkage.
- `libnfs_la_LIBADD` links protocol sublibraries, socket/pthread libs, and optional TLS/GnuTLS.

## Control Flow
Automake conditionals add `-no-undefined` for Windows and TLS include/libs when enabled.

## State And Persistence
No runtime state. Controls produced libtool archive/shared library and ABI version metadata.

## Dependencies And Integration Points
Integrates with configure checks for Win32, TLS, Kerberos, socket, and pthread libraries. Depends on sibling protocol subdirectories.

## Risks
Autotools and CMake source/dependency lists must stay aligned. Including Win32 compat source unconditionally relies on internal preprocessor guards or portable content. ABI version values require deliberate maintenance.

## Test Signals
Run `autoreconf`/configure/make with TLS, Kerberos, Win32 cross, and minimal builds; compare installed symbols and linked libraries against CMake output.
