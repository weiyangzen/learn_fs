<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/libkeyutils.pc.in -->
# sources/security-integrity/keyutils/libkeyutils.pc.in

## Purpose

`libkeyutils.pc.in` is the pkg-config template for consumers of libkeyutils. Build substitution fills `@libdir@`, `@includedir@`, and `@VERSION@`.

## Important APIs, Types, and Functions

It exports package metadata `Name`, `Description`, `Version`, compile flags `-I${includedir}`, and link flags `-L${libdir} -lkeyutils`.

## Control Flow

There is no runtime control flow; it is transformed by the build/install process into `libkeyutils.pc`.

## State and Persistence Behavior

Installed pkg-config metadata persists in the target pkg-config directory and guides downstream builds.

## Dependencies and Integration Points

It integrates with pkg-config, the project Makefile/configure substitution path, and applications using `pkg-config --cflags --libs libkeyutils`.

## Risks and Edge Cases

Incorrect substitution paths produce broken downstream compile/link flags. Missing extra private libs would affect static linking if future code adds dependencies.

## Test Signals

After install, `pkg-config --modversion libkeyutils` and `pkg-config --libs --cflags libkeyutils` should return the substituted version and usable flags.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/libkeyutils.pc.in -->
