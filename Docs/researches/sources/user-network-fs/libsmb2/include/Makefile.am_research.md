# sources/user-network-fs/libsmb2/include/Makefile.am

## Purpose
`include/Makefile.am` defines which headers are installed or distributed by the autotools build for libsmb2.

## Important APIs, Types, and Functions
`smb2dir = $(includedir)/smb2` sets the installation subdirectory. `dist_smb2_HEADERS` installs public headers: `libsmb2.h`, DCERPC headers, `libsmb2-raw.h`, `smb2.h`, and `smb2-errors.h`. `dist_noinst_HEADERS` distributes but does not install private/portability headers such as `asprintf.h`, `libsmb2-private.h`, `portable-endian.h`, and `slist.h`.

## Control Flow
Autotools expands these variables during `make dist`, `make install`, and library builds. No runtime code executes from this file.

## State and Persistence Behavior
The file affects installed filesystem layout and release tarball content. It does not create runtime state.

## Dependencies and Integration Points
It integrates with automake and must stay aligned with public CMake install headers and the library source includes. Public API additions need updates here to be installed by autotools.

## Risks and Edge Cases
`smb2-ioctl.h` is not listed in `dist_smb2_HEADERS`, so autotools installs may omit that public-looking header. Header list drift between CMake and automake can create build-system-specific API availability.

## Test Signals
Run `make distcheck` and inspect `make install DESTDIR=...` output. Confirm all headers included by public headers are available to downstream consumers.
