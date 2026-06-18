# sources/user-network-fs/libsmb2/lib/Makefile.am

## Purpose
`lib/Makefile.am` defines the autotools/libtool build for the `libsmb2.la` library.

## Important APIs, Types, and Functions
It sets `AM_CFLAGS`, `lib_LTLIBRARIES`, include CPPFLAGS, the full `libsmb2_la_SOURCES` list, libtool version components `SOCURRENT=6`, `SOREVISION=1`, `SOAGE=0`, linker flags using `-version-info`, `-no-undefined`, exported symbols from `libsmb2.syms`, optional Kerberos libraries, and distribution of `libsmb2.syms`.

## Control Flow
Automake expands variables into compile/link rules. Libtool links the listed sources into `libsmb2.la` and applies symbol export and versioning rules.

## State and Persistence Behavior
The file affects build artifacts, shared-library ABI version metadata, and install outputs. It has no runtime state.

## Dependencies and Integration Points
It integrates with autotools variables from `configure.ac`, public/private headers under `include/`, crypto/auth/protocol implementation files, and optional Kerberos link flags.

## Risks and Edge Cases
Source list drift against CMake is a maintenance risk. The indentation for `smb2-cmd-oplock-break.c` differs but is syntactically harmless. ABI version numbers must be advanced deliberately when exported symbols change.

## Test Signals
Run `autoreconf`, `./configure` with and without Kerberos, `make`, `make check` if available, `make distcheck`, and inspect exported symbols and libtool soname.
