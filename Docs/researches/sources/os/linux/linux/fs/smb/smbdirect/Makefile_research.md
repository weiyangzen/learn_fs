# File Research: sources/os/linux/linux/fs/smb/smbdirect/Makefile

Build rules for the SMBDirect support module.

Key contents:
- Builds `smbdirect.o` when `CONFIG_SMBDIRECT` is enabled.
- Aggregates SMBDirect implementation objects: `socket.o`, `connection.o`, `mr.o`, `rw.o`, `debug.o`, `connect.o`, `listen.o`, `accept.o`, `devices.o`, and `main.o`.

Role in subsystem:
- Connects the common SMBDirect object set to Kbuild so server/client RDMA transport users can import the `SMBDIRECT` namespace.
