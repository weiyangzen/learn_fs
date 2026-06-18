# sources/user-network-fs/samba/source4/torture/libsmbclient/wscript_build

## Purpose
This Waf build fragment defines the internal smbtorture module for libsmbclient API tests.

## Important APIs, types, and functions
It declares `bld.SAMBA_MODULE('TORTURE_LIBSMBCLIENT', ...)` with source `libsmbclient.c`, generated `proto.h`, subsystem `smbtorture`, init function `torture_libsmbclient_init`, and dependencies `smbclient CMDLINE_S4`.

## Control flow
During build, Waf compiles the libsmbclient torture source and links it into smbtorture as an internal module.

## State and persistence behavior
No runtime state is handled. Persistent outputs are build artifacts and generated prototypes.

## Dependencies and integration points
The declared `smbclient` dependency supplies libsmbclient APIs, while `CMDLINE_S4` supplies torture command-line credential integration.

## Risks and edge cases
If the dependency list misses libraries used by POSIX, loadparm, or credentials code, the module can fail at link time. Since all tests are in one source file, excluding it removes the entire suite.

## Test signals
Successful module build and registration expose the `libsmbclient` suite in smbtorture.
