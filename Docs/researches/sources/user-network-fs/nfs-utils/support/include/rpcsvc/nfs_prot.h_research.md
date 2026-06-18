# sources/user-network-fs/nfs-utils/support/include/rpcsvc/nfs_prot.h

## Purpose
Rpcgen-generated NFSv2 protocol header containing constants, XDR type declarations, and client/server stubs for program 100003 version 2.

## Important APIs, Types, and Functions
Defines NFS status and file type enums, filehandle, attributes, argument/result structs for NFSv2 procedures, XDR prototypes, `NFS_PROGRAM`, `NFS_VERSION`, and `nfsproc_*_2` client/server prototypes.

## Control Flow
RPC clients and servers marshal data through the declared `xdr_*` functions and call/implement the procedure stubs for NULL, GETATTR, SETATTR, LOOKUP, READ, WRITE, CREATE, REMOVE, RENAME, LINK, SYMLINK, MKDIR, RMDIR, READDIR, and STATFS.

## State and Persistence Behavior
No runtime state in the header. Structures define the wire format and must remain compatible with generated XDR implementation.

## Dependencies and Integration Points
Included by `nfslib.h` and RPC modules. Depends on `<rpc/rpc.h>` and rpcgen conventions.

## Risks and Edge Cases
Manual edits to generated layouts break wire compatibility. `struct entry` name conflicts with libc `search.h`, as seen in `v4clients.c` workaround.

## Test Signals
Compile generated XDR sources, run NFSv2 RPC marshalling tests, and verify procedure table integration.
