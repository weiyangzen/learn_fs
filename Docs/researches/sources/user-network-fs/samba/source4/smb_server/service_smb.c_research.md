# Research: sources/user-network-fs/samba/source4/smb_server/service_smb.c

Purpose: registers and initializes the Samba 4 SMB server service task.

Control flow: `server_service_smb_init()` obtains the loadparm context, initializes NTVFS and shares, and registers service `smb` with task details that inhibit fork-on-accept and pre-fork. `smbsrv_task_init()` sets the process title, binds sockets either to configured interfaces when `bind interfaces only` is true or to wildcard addresses otherwise, registers the messaging name `smb_server`, and terminates the task on startup failure.

State and dependencies: it opens listening sockets through `smbsrv_add_socket()` and registers the service in Samba's process model. It depends on loadparm, network interface discovery, service task APIs, stream service support, NTVFS, and share initialization.

Risks and test signals: binding failure on any selected address aborts the whole SMB task. Interface configuration and wildcard discovery are common integration risk points. Signals include successful smbd startup, socket binding, and acceptance of SMB connections in selftests.
