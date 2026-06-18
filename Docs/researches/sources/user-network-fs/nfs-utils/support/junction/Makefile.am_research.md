# sources/user-network-fs/nfs-utils/support/junction/Makefile.am

## Purpose
Automake metadata that defines which private headers or support sources are built in this directory and marks generated `Makefile.in` for maintainer cleanup.

## Important APIs, Types, and Functions
No C APIs are defined. The meaningful variables are `SUBDIRS`, `noinst_HEADERS`, `noinst_LIBRARIES`, `noinst_LTLIBRARIES`, and per-library source lists.

## Control Flow
During autoreconf/automake, this file is expanded into a makefile fragment. Recursive subdirectories are entered first when `SUBDIRS` is set, and listed headers/sources are packaged into private build artifacts.

## State and Persistence Behavior
No runtime state exists. Build artifacts such as `Makefile.in`, static libraries, or libtool archives are generated outside this source file.

## Dependencies and Integration Points
Integrates with the nfs-utils autotools build. Correctness is visible through generated make rules and successful compilation of dependent support libraries.

## Risks and Edge Cases
The main risk is drift between source files and the Automake lists, which can omit headers from distribution or omit sources from a support library.

## Test Signals
Run autoreconf/automake, `make distcheck` or a clean build, and verify all listed headers and support sources are included in generated makefiles.
