<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/util/clilsa.c -->
# sources/user-network-fs/samba/source4/libcli/util/clilsa.c

Purpose: provides convenience LSA RPC helpers over SMB1 and SMB2 file sharing connections for SID/name lookup and account-right management.

Important APIs and types: `struct smblsa_state`, `smblsa_connect`, `smb2lsa_connect`, `smblsa_sid_privileges`, `smb2lsa_sid_privileges`, `smblsa_sid_check_privilege`, `smb2lsa_sid_check_privilege`, `smblsa_lookup_sid`, `smblsa_lookup_name`, `smblsa_sid_add_privileges`, and `smblsa_sid_del_privileges`. It depends on LSARPC NDR stubs, DCERPC over SMB pipes, security descriptors, SID helpers, and smbX signing protection.

Control flow: SMB1 setup connects to IPC$, opens and binds `lsarpc`, then opens an LSA policy handle. SMB2 setup opens the same named pipe over an existing SMB2 tree and calls OpenPolicy2. The public helpers lazy-connect, perform one RPC, validate both transport status and RPC result, and translate outputs such as rights arrays, `DOMAIN\name`, or SID strings.

State and persistence: connection state is cached on `cli->lsa` or `tree->lsa`, including binding handle and policy handle. Privilege add/delete calls persist account-right changes on the remote server.

Risks: cached handles can become stale if the underlying tree/session dies. Lookup validation assumes one domain and one result; malformed server replies return invalid network response. Add/delete require powerful remote access. Test signals include IPC$ connection failure, OpenPolicy result failure, SID parsing errors, lookup response shape validation, SMB2 parity, and add/remove rights round trips.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/util/clilsa.c -->
