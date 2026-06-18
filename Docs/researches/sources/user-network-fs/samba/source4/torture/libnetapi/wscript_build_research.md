# sources/user-network-fs/samba/source4/torture/libnetapi/wscript_build

## Purpose
This Waf build fragment defines the internal smbtorture module for libnetapi tests.

## Important APIs, types, and functions
It calls `bld.SAMBA_MODULE('TORTURE_LIBNETAPI', ...)` with sources `libnetapi.c`, `libnetapi_user.c`, `libnetapi_group.c`, and `libnetapi_server.c`, autogenerates `proto.h`, sets subsystem `smbtorture`, and names `torture_libnetapi_init` as the init function.

## Control flow
At build configuration time, Waf consumes this module declaration to compile the listed sources into an internal smbtorture module.

## State and persistence behavior
The file does not manage runtime state. Build artifacts and generated prototypes are its persistent output.

## Dependencies and integration points
Declared dependencies are `netapi` and `CMDLINE_S4`, which connect these source4 torture tests to source3 libnetapi and command-line credential support.

## Risks and edge cases
Missing a source file or dependency here would make tests unavailable or fail at link time. The module is internal, so it is expected to be loaded through smbtorture rather than installed as a standalone binary.

## Test signals
Successful build and module registration expose the `netapi` suite and ensure all three functional NetAPI test files are compiled together.
