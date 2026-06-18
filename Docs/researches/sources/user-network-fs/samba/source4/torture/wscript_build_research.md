<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/wscript_build -->
# sources/user-network-fs/samba/source4/torture/wscript_build

## Purpose

This is the main Waf build script for Samba4 torture binaries and modules. It defines shared torture support, core smbtorture modules, subdirectory recursion, and standalone test tools such as `smbtorture`, `gentest`, `masktest`, and `locktest`.

## Important APIs, Types, and Functions

- `bld.SAMBA_SUBSYSTEM()` declares shared subsystems such as `TORTURE_UTIL`, `TORTURE_NDR`, `IREMOTEWINSPOOL_COMMON`, and `torturemain`.
- `bld.SAMBA_MODULE()` declares smbtorture modules including `TORTURE_BASIC`, `TORTURE_RAW`, `torture_rpc`, `TORTURE_RAP`, `TORTURE_AUTH`, `TORTURE_LDAP`, `TORTURE_NBT`, and `TORTURE_VFS`.
- `bld.RECURSE()` includes sub-builds for `smb2`, `winbind`, `libnetapi`, `libsmbclient`, `gpo`, `drs`, `dns`, `local`, and `krb5`.
- `bld.SAMBA_BINARY()` declares `smbtorture`, `gentest`, `masktest`, and `locktest`.

## Control Flow

The script computes Python embedded library names, builds utility subsystems, defines modules with source lists and dependency lists, conditionally adds NTVFS-specific spoolss notify sources, recurses into child directories, assembles `TORTURE_MODULES`, and links those modules into `torturemain` and `smbtorture`. Module declarations include `init_function` names that register suites at runtime.

## State and Persistence Behavior

This file controls build graph state and generated prototype headers. It has no runtime persistence, but changes affect which tests are compiled, linked, and available in `smbtorture`.

## Dependencies and Integration Points

It integrates almost every Samba4 torture subsystem with Waf, generated NDR bindings, RPC client libraries, Kerberos/auth libraries, SMB client libraries, process/service helpers, and Python embedding. The `TORTURE_VFS` stanza includes `vfs/vfs.c`, `fruit.c`, `acl_xattr.c`, and `streams_xattr.c`; `bld.RECURSE('winbind')` brings in the winbind torture module.

## Risks and Edge Cases

Large hand-maintained source/dependency lists can drift when files move or add new link dependencies. Conditional `enabled=bld.PYTHON_BUILD_IS_ENABLED()` affects test availability. The NTVFS conditional changes RPC module contents based on build config.

## Test Signals

Pass signals are successful Waf configure/build, generated prototype headers, linked `smbtorture`, and runtime visibility of all expected suites. Missing modules or unresolved symbols usually indicate stale source/dependency declarations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/wscript_build -->
