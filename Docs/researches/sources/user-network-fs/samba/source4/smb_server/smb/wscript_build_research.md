# sources/user-network-fs/samba/source4/smb_server/smb/wscript_build

## Purpose
Defines the Waf build subsystem for the SMB1 protocol implementation under `source4/smb_server/smb`. It collects the C files in this directory into the `SMB_PROTOCOL` subsystem, declares generated prototypes, and gates the subsystem on the NTVFS file server build option.

## Important APIs, Types, And Functions
- `bld.SAMBA_SUBSYSTEM('SMB_PROTOCOL', ...)` is the only build declaration.
- `source=` lists `receive.c`, `negprot.c`, `nttrans.c`, `reply.c`, `request.c`, `search.c`, `service.c`, `sesssetup.c`, `srvtime.c`, `trans2.c`, and `signing.c`.
- `autoproto='smb_proto.h'` requests automatic prototype generation for the subsystem.
- `deps='dfs_server_ad'` and `public_deps='ntvfs LIBPACKET samba-credentials samba_server_gensec'` encode internal and public link dependencies.
- `enabled=bld.CONFIG_SET('WITH_NTVFS_FILESERVER')` builds the subsystem only when the NTVFS file server is enabled.

## Control Flow
There is no runtime control flow. At build configuration time Waf evaluates `WITH_NTVFS_FILESERVER`; if true, it compiles the listed source files as `SMB_PROTOCOL` and exposes their generated prototypes.

## State And Persistence
No runtime state. Build state includes the subsystem membership and dependency graph. Changes here affect which source files participate in generated prototypes and linking.

## Dependencies And Integration Points
Integrates the SMB1 frontend with NTVFS, packet streaming, credentials, GENSEC, and DFS referral support. The generated `smb_proto.h` is included by `smb_server.h`, making functions visible across the source files in this subsystem.

## Risks
Forgetting to add a new source file here would produce missing symbols or missing prototypes. Removing a dependency can create link or configuration-only failures. Because `trans2.c` depends on DFS AD support, the explicit `dfs_server_ad` dependency is significant. The entire SMB1 protocol frontend disappears when `WITH_NTVFS_FILESERVER` is disabled, so packaging/tests must account for that configuration.

## Test Signals
Build with `WITH_NTVFS_FILESERVER` enabled and disabled, verify `smb_proto.h` generation, and run link checks for references to NTVFS, packet, credentials, GENSEC, and DFS referral symbols.
