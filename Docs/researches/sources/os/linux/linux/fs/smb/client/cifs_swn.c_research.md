# File Research: sources/os/linux/linux/fs/smb/client/cifs_swn.c

Service Witness Notification client integration for CIFS high-availability shares.

Registrations are stored in a global IDR protected by `cifs_swnreg_idr_mutex`; `struct cifs_swn_reg` records registration id, refcount, network/share names, notification flags, and tcon. Registration lookup deduplicates by extracted host/share names.

`cifs_swn_send_register_message()` and `_unregister_message()` send generic-netlink multicast messages to userspace with registration id, network/share name, server IP, notification flags, and authentication info. Kerberos is represented by a flag; NTLM variants include username/password/domain when present.

Incoming `cifs_swn_notify()` validates registration id and notification type, then handles resource state changes by signaling reconnect, and client-move notifications by storing a new SWN destination address, unregistering from the old address, registering for the new one, and reconnecting.

Address handling preserves the previous SMB port while switching IPv4/IPv6 addresses. `cifs_swn_dump()` renders registrations into seq_file output, and `cifs_swn_check()` resends register messages for all current registrations.
