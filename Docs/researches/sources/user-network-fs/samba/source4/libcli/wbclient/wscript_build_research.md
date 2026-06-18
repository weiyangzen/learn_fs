<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/wbclient/wscript_build -->
# sources/user-network-fs/samba/source4/libcli/wbclient/wscript_build

Purpose: defines the waf build target for the old source4 winbind client adapter library.

Important APIs and types: `bld.SAMBA_LIBRARY('LIBWBCLIENT_OLD', ...)` builds `wbclient.c` as a private library with public deps `samba-errors events wbclient`, private deps `WB_REQTRANS NDR_WINBIND MESSAGING RPC_NDR_WINBIND`, and a cflag defining `WINBINDD_SOCKET_DIR`.

Control flow: during configure/build, waf interpolates `bld.env.WINBINDD_SOCKET_DIR` into a C preprocessor define and compiles the source into a private Samba library.

State and persistence: build metadata only; it changes which object/library products exist and which socket-dir constant the C code sees.

Risks: dependency drift or a missing environment value can break builds. The target is private, so downstream public consumers should not link it directly. Test signals include waf target generation, correct cflag quoting, and linkage of the wbclient conversion functions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/wbclient/wscript_build -->
