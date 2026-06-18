# sources/user-network-fs/libsmb2/examples/smb2-raw-getsd-async.c

Purpose: This raw async example retrieves and prints a file or directory security descriptor over SMB2.

Important APIs and types: It uses compound CREATE/QUERY_INFO/CLOSE, `SMB2_0_INFO_SECURITY`, `SMB2_READ_CONTROL`, owner/group/DACL security flags, `struct smb2_security_descriptor`, `smb2_sid`, `smb2_acl`, `smb2_ace`, and helper printers for SID, ACE, ACL, and descriptor control flags.

Control flow: The program connects to the target share, queues a compound request that opens the path with read-control access, queries security info into a decoded descriptor, closes the handle, waits via poll/service, prints descriptor revision/control/owner/group/DACL entries, frees decoded data, and disconnects.

State and persistence behavior: It only reads remote security metadata. Runtime state includes callback status, retained security descriptor pointer, and temporary compound request data.

Dependencies and integration points: It validates raw security info querying, security descriptor decoding, compound PDU file-id substitution, and DACL/SID data structures.

Risks: It requests owner, group, and DACL only, not SACL, so auditing information is not covered. Printer support handles common ACE types and emits "can't print this type" for others. Error paths call `exit`, skipping cleanup.

Test signals: Against files with known ACLs, printed SIDs, ACE counts, masks, and control bits should match server ACL tools. Access-denied tests validate `SMB2_READ_CONTROL` handling.
