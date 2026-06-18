# File Research: sources/os/linux/linux-stable/fs/nfsd/nfsd.h

## Summary
Central NFSD header collecting service constants, service entry points, NFS status constants, NFSv4 attribute masks, and compile-time stubs for optional features.

## Contents
Defines NFSD protocol version bounds, block-size limits, compound sizing constants, server thread helpers, nfsdfs client directory helpers, version toggling APIs, debugfs hooks, IO mode globals, lockd hooks, NFSv4 state lifecycle declarations, and pre-XDR’d `nfserr_*` status macros.

## Important Details
`nfsd_programs[]` and `nfsd_version{2,3,4}` are declared here for SunRPC service registration. `struct nfsd_thread_local_info` carries per-thread duplicate-reply-cache state. `nfsd_v4client()` and `nfsd_user_namespace()` are shared helpers used by protocol and XDR code. NFSv4 supported, writable, and exclusive-create attribute masks are centralized here.

## Risks
This header is a broad internal contract. Changes to error macros, attribute masks, version constants, or optional-feature stubs affect many protocol files. Attribute masks must remain aligned with XDR decoding/encoding support, or clients can be told an attribute is supported when NFSD cannot process it correctly.
