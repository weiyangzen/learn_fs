# sources/user-network-fs/samba/source4/smb_server/smb2/wscript_build

## Purpose
This Waf build fragment defines the source4 SMB2 protocol subsystem build target. It collects SMB2 server implementation files into `SMB2_PROTOCOL`, declares generated prototypes, dependencies, and the feature gate for the NTVFS file server.

## Important APIs, Types, And Functions
The file calls `bld.SAMBA_SUBSYSTEM('SMB2_PROTOCOL', ...)` with source files `receive.c negprot.c sesssetup.c tcon.c fileio.c fileinfo.c find.c keepalive.c`, `autoproto='smb2_proto.h'`, and public dependencies `ntvfs LIBPACKET LIBCLI_SMB2 samba_server_gensec NDR_DFSBLOBS`.

## Control Flow
At configure/build time, Waf evaluates this fragment when recursing into `smb2`. The subsystem is enabled only when `bld.CONFIG_SET('WITH_NTVFS_FILESERVER')` is true. Autoproto generation produces declarations consumed by `smb2_server.h`.

## State And Persistence
It changes build graph state, not runtime state. Generated prototype headers and compiled objects are build artifacts outside source logic.

## Dependencies And Integration Points
The target is pulled in by `source4/smb_server/wscript_build`, and the parent `SMB_SERVER` subsystem publicly depends on `SMB2_PROTOCOL`. Dependency declarations expose NTVFS, packet transport, SMB2 client/common helpers, GENSEC server support, and DFS blob NDR support to these sources.

## Risks And Test Signals
Risks include source-list drift when adding SMB2 commands, missing public dependencies masked by include order, and the subsystem disappearing when `WITH_NTVFS_FILESERVER` is false. Build tests should verify autoproto generation, a full `WITH_NTVFS_FILESERVER` build, and disabled-feature builds that omit SMB2 server objects cleanly.
