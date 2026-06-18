<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/wscript_build -->
# sources/user-network-fs/samba/source4/libcli/wscript_build

Purpose: top-level waf build description for source4 libcli subsystems and libraries relevant to SMB, LSA, WINS replication, resolve, and raw SMB clients.

Important APIs and types: recursive builds for `ldap`, `wbclient`, `smb2`, and `rap`; subsystem targets `LIBSAMBA_TSOCKET`, `LIBCLI_LSA`, `cli_composite`, `LIBCLI_SMB_COMPOSITE`, `LIBCLI_DGRAM`, `LIBCLI_WREPL`, `LIBCLI_RESOLVE`, `LP_RESOLVE`, `LIBCLI_FINDDCS`, `LIBCLI_SMB`; and library target `smbclient-raw`.

Control flow: waf evaluates target declarations, source lists, generated autoprotos, private headers, public deps, and private deps. `LIBCLI_SMB_COMPOSITE` collects loadfile, savefile, connect_nego, connect, sesssetup, fetchfile, appendacl, fsinfo, and smb2 composite sources.

State and persistence: build graph only. It determines generated prototype headers and link relationships. Several runtime modules depend on targets defined here, such as raw SMB depending on composite helpers and WINS replication depending on tstream support.

Risks: cyclic or duplicated deps can cause build instability; `LIBCLI_DGRAM` lists `LIBCLI_RESOLVE` twice. Private header declarations affect install/API visibility. Test signals include full waf configure/build, generated `clilsa.h` and `winsrepl_proto.h`, and link tests for consumers of `LIBCLI_SMB` and `LIBCLI_WREPL`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/wscript_build -->
