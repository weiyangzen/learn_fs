# File Research: sources/os/linux/linux/fs/nfsd/nfs4xdr_gen.h

## Summary
Generated header declaring the `xdrgen` helper functions consumed by NFSD NFSv4 XDR code.

## Contents
The header includes Linux base types, SunRPC XDR declarations, xdrgen builtins, and generated NFSv4.1 type definitions. It declares encode/decode helpers for open-arguments attributes, delegated access/modify times, ACL model/scope enums, POSIX ACL tags, and POSIX ACL permissions.

## Important Details
The include guard is `_LINUX_XDRGEN_NFS4_1_DECL_H`. Comments identify `Documentation/sunrpc/xdr/nfs4_1.x` as the source and state that manual edits will be lost.

## Risks
Consumers depend on this header matching `nfs4xdr_gen.c` and the generated xdrgen type headers. Manual changes would be overwritten and could desynchronize the NFSv4 XDR helper ABI inside NFSD.
