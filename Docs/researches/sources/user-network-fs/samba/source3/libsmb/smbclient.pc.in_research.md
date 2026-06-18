# sources/user-network-fs/samba/source3/libsmb/smbclient.pc.in

Purpose: `smbclient.pc.in` is the pkg-config template for the installed `libsmbclient` development package. Configure/waf substitution fills installation prefixes, version, rpath flags, and include/lib directories.

Important fields: it defines `prefix`, `exec_prefix`, `libdir`, and `includedir`; package metadata `Name: smbclient`, `Description: A SMB library interface`, `Version: @PACKAGE_VERSION@`, and `URL`; linker flags `Libs: @LIB_RPATH@ -L${libdir} -lsmbclient`; and compiler flags `Cflags: -I${includedir}`.

Control flow and integration: this file is consumed by Samba's build/install process, referenced by the `libsmb/wscript` `pc_files='smbclient.pc'` setting. Downstream projects use the generated `smbclient.pc` via `pkg-config --cflags --libs smbclient`.

State and persistence: no runtime state. The generated `.pc` file is an installed build artifact and encodes the installation layout.

Dependencies: depends on build-time substitution variables and the installed `libsmbclient` library/header set.

Risks: incorrect `libdir`, `includedir`, version, or rpath substitution breaks downstream builds. Overly broad `Libs` can leak private dependencies; here the template exposes only `-lsmbclient` plus configured rpath.

Test signals: packaging tests should run `pkg-config --exists smbclient`, check version output, compile a tiny program including `libsmbclient.h`, and verify link flags resolve `libsmbclient`.
