# File Research: sources/os/linux/linux/fs/smb/server/Makefile

This Makefile builds the `ksmbd` module/object when `CONFIG_SMB_SERVER` is enabled.

Key contents:
- `obj-$(CONFIG_SMB_SERVER) += ksmbd.o`.
- Core object list includes Unicode, auth, VFS, oplock, connection, work, crypto context, management modules, IPC/TCP transports, ACL, SMB2 PDU/ops/misc, and ASN.1-generated SPNEGO decoders.
- Adds explicit dependencies so `asn1.o` waits for generated ASN.1 headers.
- Conditionally includes `transport_rdma.o` for SMB Direct and `proc.o` for procfs support.

This file shows the group’s modules are early/core KSMBD infrastructure rather than standalone utilities.
