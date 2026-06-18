# sources/user-network-fs/samba/source4/libcli/rap/wscript_build

Purpose: Waf build definition for the `LIBCLI_RAP` subsystem.

Important configuration: builds `rap.c`, declares public dependencies on `smbclient-raw` and `NDR_RAP`, and generates `proto.h`.

Control flow and state: no runtime logic; it controls compile/link placement for RAP client support.

Dependencies and integration: ensures RAP wrappers can call raw SMB transaction code and generated RAP NDR codecs.

Risks: dependency drift causes build or link failures. Test signals include Waf target build and consumers that include `libcli/rap/proto.h`.
