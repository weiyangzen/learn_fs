# sources/user-network-fs/samba/source3/utils/smbfilter.c

`smbfilter.c` is a debugging SMB TCP proxy. It listens locally on port 445, forks per client, connects to a destination SMB server, forwards raw SMB packets in both directions, and can inspect or modify NetBIOS session requests, SMB negotiate replies, and SMB session setup requests.

Important functions are `filter_request`, `filter_reply`, `send_smb`, `filter_child`, `start_filter`, and `save_file`. `filter_request` can rewrite the destination NetBIOS name in a session request and saves session setup password/session bytes to `sessionsetup.dat`. `filter_reply` has hooks for security/capability bit manipulation. `filter_child` polls client and server sockets, receives raw packets, filters, and forwards them.

State is per-process sockets plus optional global `netbiosname`. Persistent side effects are `sessionsetup.dat` and `sessionsetup1.dat` in the working directory. Dependencies include Samba socket helpers, NetBIOS name parsing/mangling, SMB packet macros, polling wrappers, and raw SMB receive/write helpers.

Risks include binding privileged port 445, unbounded forking, sensitive session setup captures, potentially protocol-breaking macro changes, and the use of `system("mv ...")`. Test signals: proxying a real test connection, NetBIOS rewrite, bidirectional disconnect handling, captured session setup files, and destination resolution.
