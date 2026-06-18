# sources/user-network-fs/libnfs/lib/CMakeLists.txt

## Purpose
CMake build definition for the libnfs library target.

## Important APIs, Types, And Functions
- Defines `SOURCES` including `init.c`, `krb5-wrapper.c`, core libnfs, ZDR, multithreading, NFSv3/v4, PDU, and socket sources.
- Adds Windows resource/def files when building shared libraries on Windows.
- Creates target `nfs`, links core/system libraries, sets version/SOVERSION, output name, and install destinations.

## Control Flow
Configure-time logic builds the source list, conditionally appends Windows metadata, creates the library, applies target properties, and registers install/export rules.

## State And Persistence
No runtime state. Build artifacts include a library named `nfs` with output name `libnfs` and installed binary/archive/library files.

## Dependencies And Integration Points
Consumes top-level CMake variables `CORE_LIBRARIES`, `SYSTEM_LIBRARIES`, `PROJECT_VERSION`, `SOVERSION`, and `CMAKE_INSTALL_LIBDIR`.

## Risks
Setting `PREFIX ""` to avoid `liblibnfs.so` is nonstandard and should be validated across Unix, macOS, and Windows generators. `krb5-wrapper.c` is always in the source list but compiles to empty content without `HAVE_LIBKRB5`.

## Test Signals
Configure/build shared and static libraries on Unix and Windows, inspect output filenames, install/export package, and build with Kerberos enabled/disabled.
