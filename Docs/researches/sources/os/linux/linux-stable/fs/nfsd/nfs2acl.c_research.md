# File Research: sources/os/linux/linux-stable/fs/nfsd/nfs2acl.c

## Summary
Implements NFSACL protocol version 2 server procedures over POSIX ACLs.

## Main APIs
Defines procedures for `NULL`, `GETACL`, `SETACL`, `GETATTR`, and `ACCESS`, plus `nfsd_acl_version2`.

## Behavior
`GETACL` verifies the filehandle, validates the ACL mask, collects file attributes, returns access and/or default ACLs, and synthesizes a minimum ACL from mode when no access ACL exists. `SETACL` verifies setattr permission, takes a write reference, locks the inode, and sets access and default POSIX ACLs. XDR decode/encode uses legacy NFSv2 filehandle and attr helpers plus Linux NFS ACL stream helpers.

## Risks
Version 2 maps an invalid ACL mask to `nfserr_io` in `GETACL`, unlike the NFSv3 ACL path. `SETACL` releases decoded ACLs regardless of success, so ownership transfer between decoder and procedure must remain consistent.
