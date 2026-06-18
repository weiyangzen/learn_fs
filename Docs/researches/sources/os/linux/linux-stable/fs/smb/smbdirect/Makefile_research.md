# File Research: sources/os/linux/linux-stable/fs/smb/smbdirect/Makefile

## Summary
Builds the common SMB Direct support object set when `CONFIG_SMBDIRECT` is enabled.

## Main Responsibilities
- Add `smbdirect.o` to the build for `CONFIG_SMBDIRECT`.
- Compose `smbdirect-y` from socket, connection, memory registration, RDMA read/write, debug, connect/listen/accept, device, and main implementation objects.

## Cross-File Interactions
Produces the common SMB Direct implementation imported by ksmbd server RDMA transport and CIFS client SMB Direct wrappers.

## Risks
Object list changes must stay synchronized with the common SMB Direct API surface; missing objects would cause link failures or incomplete RDMA transport support.
