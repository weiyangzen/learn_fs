# sources/user-network-fs/samba/source3/libsmb/wscript

Purpose: this waf build script defines the Samba3 `smbclient` shared library target for `libsmbclient`.

Important build API: `build(bld)` calls `bld.SAMBA3_LIBRARY('smbclient', ...)` with source files `libsmb_cache.c`, compatibility/context/dir/file/misc/path/printjob/server/stat/xattr/setget modules, public dependencies, public header `../include/libsmbclient.h`, ABI directory `ABI`, ABI symbol match `smbc_*`, version `0.8.1`, and pkg-config file `smbclient.pc`.

Control flow and integration: waf imports and executes `build` during Samba configuration/build. The target aggregates the public libsmbclient API rather than the internal Python binding or socket helper files in this subset. Public dependencies include `pthread`, `talloc`, `smbconf`, `libsmb`, `KRBCLIENT`, `msrpc3`, and `libcli_lsa3`.

State and persistence: no runtime state. The script produces build artifacts, installed public headers, ABI checks, and pkg-config output.

Risks: changing the source list can omit part of libsmbclient or accidentally expose private code. ABI metadata matters because public `smbc_*` symbols are versioned. Dependency changes affect downstream link behavior.

Test signals: waf configure/build should generate `libsmbclient`, run ABI checks against `ABI`, install `libsmbclient.h`, generate `smbclient.pc`, and link a downstream sample via pkg-config.
