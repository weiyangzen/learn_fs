<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/wscript_build -->
# sources/user-network-fs/samba/source3/torture/wscript_build

## Purpose
`wscript_build` defines Samba source3 torture/test binaries for waf, including `smbtorture3`, standalone message and passdb tests, `locktest2`, `vfstest`, and an RPC SAMR test.

## Important APIs, types, and functions
- `bld.SAMBA3_BINARY()` entries describe binary names, source lists, dependencies, install/selftest flags, and cflags.
- `TORTURE3_ADDITIONAL_SOURCE` conditionally adds `test_ctdbd_conn.c` when CTDB support is enabled.
- `SMB1_SOURCES` conditionally adds `vfstest_chain.c` when `WITH_SMB1SERVER` is configured.
- `smbtorture` receives `-DWINBINDD_SOCKET_DIR="..."` for async winbind tests.

## Control flow
The build script evaluates feature flags, composes source-list strings, and registers targets. `smbtorture` aggregates many torture source files including `utable.c` and `wbc_async.c`. `vfstest` always includes `cmd_vfs.c` and `vfstest.c`, and includes SMB1 chain tests only for SMB1 server builds.

## State and persistence behavior
This is build metadata rather than runtime code. It controls which generated build outputs exist and which binaries are marked for selftest. Runtime persistence is unaffected except through compiled feature availability.

## Dependencies and integration points
The targets depend on Samba build-system facilities and libraries such as `talloc`, `smbconf`, `libsmb`, `msrpc3`, `WB_REQTRANS`, `LOCKING`, `vfs`, `CMDLINE_S3`, `SMBREADLINE`, `pdb`, `AUTH_COMMON`, `auth`, and `cmocka`.

## Risks and edge cases
- Conditional source inclusion must match C declarations; building `vfstest_chain.c` without SMB1 parser support would fail.
- `smbtorture` has a broad source list, so dependency omissions can appear only under specific feature configurations.
- `WINBINDD_SOCKET_DIR` is compiled into `smbtorture`; selftests override it at runtime through `wbc_async.c` only when nss-wrapper is enabled.

## Test signals
Successful waf configuration/build and Samba selftest discovery of `smbtorture`, `vfstest`, `locktest2`, and `test_rpc_samr` are the main signals. Feature matrix builds with and without CTDB and SMB1 validate conditional paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/wscript_build -->
