# sources/user-network-fs/samba/source4/torture/smb2/wscript_build

## Purpose
`wscript_build` declares the Samba build target for the SMB2 torture module. It tells waf which SMB2 torture source files form the `TORTURE_SMB2` internal module and how that module integrates into the `smbtorture` subsystem.

## Important APIs, Types, and Functions
The file calls `bld.SAMBA_MODULE('TORTURE_SMB2', ...)`. Its source list includes all SMB2 torture implementations in this directory, including `streams.c`, `tcon.c`, `timestamps.c`, and `util.c`. Build metadata sets `subsystem='smbtorture'`, `deps='LIBCLI_SMB2 torture NDR_IOCTL CMDLINE_S4'`, `internal_module=True`, `autoproto='proto.h'`, and `init_function='torture_smb2_init'`.

## Control Flow
At configure/build time, waf evaluates this Python-style build script, collects the listed source files, generates `proto.h` declarations, and builds an internal module initialized through `torture_smb2_init`. Runtime test registration happens in the compiled C files, but this build file is what makes those registration functions available to smbtorture.

## State and Persistence Behavior
The file has no runtime state. Its persistent effect is build graph state: object compilation membership, generated prototype output, dependency linkage, and internal module metadata.

## Dependencies and Integration Points
It integrates SMB2 tests with Samba's waf build system and the broader smbtorture module loader. The explicit dependencies provide SMB2 client APIs, torture harness APIs, ioctl NDR definitions, and Samba command-line support.

## Risks
Removing a source file from this list silently drops tests from the SMB2 module. Adding a source without the right dependencies can cause compile or link failures. The `autoproto` setting means function signatures exported by source files affect generated headers consumed by sibling tests.

## Test Signals
Build success confirms the source list and dependencies are coherent. At runtime, `smbtorture --list-suites` or `--list` should expose SMB2 suites only if this module built and initialized correctly.
