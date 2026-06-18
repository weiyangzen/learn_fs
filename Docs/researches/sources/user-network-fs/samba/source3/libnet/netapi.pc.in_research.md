# sources/user-network-fs/samba/source3/libnet/netapi.pc.in

## Purpose

Pkg-config template for Samba's `libnetapi` client library.

## Important APIs, Types, and Functions

Defines substitution variables `prefix`, `exec_prefix`, `libdir`, and `includedir`, plus pkg-config fields `Name`, `Description`, `Version`, `Libs`, `Cflags`, and `URL`. `@PACKAGE_VERSION@` and `@LIB_RPATH@` are build-time substitutions.

## Control Flow

No runtime control flow. The build/install process expands this template into a `.pc` file for `pkg-config` consumers.

## State and Persistence Behavior

The installed `.pc` file persists library path, include path, rpath/linker flags, and version metadata. Consumers use it to compile and link against `-lnetapi`.

## Dependencies and Integration Points

Integrates Samba's install layout with external build systems through `pkg-config`.

## Risks and Test Signals

Risks include stale path substitution, missing rpath flags, or packaging mismatches. Test signals are `pkg-config --cflags --libs netapi` and a successful external compile/link against libnetapi.
