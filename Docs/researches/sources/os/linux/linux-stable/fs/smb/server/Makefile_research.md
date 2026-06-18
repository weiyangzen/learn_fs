# File Research: sources/os/linux/linux-stable/fs/smb/server/Makefile

Read status: complete.

## Purpose
Builds the `ksmbd` module/object list for the in-kernel SMB3 server.

## Main Contents
- Adds `ksmbd.o` under `CONFIG_SMB_SERVER`.
- Lists core server, auth, VFS, oplock, connection, work, management, transport, ACL, SMB2 PDU, and generated ASN.1 objects.
- Declares dependencies for generated SPNEGO ASN.1 headers/sources.
- Conditionally includes RDMA transport and proc support.

## Dependencies And Role
Defines compilation composition for the server subtree and generated ASN.1 integration.

## Risks
Object ordering and generated-header dependencies matter for clean parallel builds. Missing objects silently remove feature implementations from the final module.
