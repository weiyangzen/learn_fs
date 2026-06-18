# File Research: sources/os/linux/linux/fs/nfsd/nfs4xdr_gen.c

## Summary
Generated `xdrgen` support code for a subset of NFSv4.1 XDR declarations used by NFSD's hand-written `nfs4xdr.c`. It is generated from `Documentation/sunrpc/xdr/nfs4_1.x` and explicitly warns that manual edits will be lost.

## Main APIs
- `xdrgen_decode_fattr4_open_arguments()` / `xdrgen_encode_fattr4_open_arguments()`.
- `xdrgen_decode_fattr4_time_deleg_access()` / `xdrgen_encode_fattr4_time_deleg_access()`.
- `xdrgen_decode_fattr4_time_deleg_modify()` / `xdrgen_encode_fattr4_time_deleg_modify()`.
- `xdrgen_decode_aclmodel4()` / `xdrgen_encode_aclmodel4()`.
- `xdrgen_decode_aclscope4()` / `xdrgen_encode_aclscope4()`.
- `xdrgen_decode_posixacetag4()` / `xdrgen_encode_posixacetag4()`.
- `xdrgen_decode_posixaceperm4()` / `xdrgen_encode_posixaceperm4()`.

## Behavior
The file wraps generic xdrgen builtins for integers, booleans, hyper values, opaque strings, UTF-8 strings, bitmaps, and NFS times, then layers NFSv4-specific enum validation and structure traversal on top.

Enum decoders validate incoming values for open argument bit categories, delegation types, ACL models, ACL scopes, and POSIX ACL tags before storing them. Encoders write enum values directly as u32s because local callers are expected to provide valid constants.

The exported open-arguments encoder/decoder handles five bitmap arrays describing supported OPEN share access, share deny, delegation-want, claim, and create-mode choices. Delegated timestamp attributes are encoded/decoded as NFS time structures. POSIX ACL helper functions encode/decode tag, permission, and owner-name elements, with internal array helpers for default and access ACL forms.

## Dependencies
Includes Linux SunRPC svc/XDR headers, `nfs4xdr_gen.h`, and generated xdrgen type definitions from `linux/sunrpc/xdrgen/nfs4_1.h`.

## Risks
This file must stay synchronized with the generated header and the XDR specification. Bounds for generated bitmap and array element storage are determined by generated type definitions, so callers must use those structures as intended.

Because only a subset of generated helpers is exported, `nfs4xdr.c` still owns most protocol-specific validation, memory allocation, and Linux object conversion.
