# sources/user-network-fs/libsmb2/examples/smb2-share-enum-sync.c

Purpose: This synchronous example enumerates SMB shares on a server through the SRVSVC RPC helper.

Important APIs and types: It uses `getopt`, `smb2_connect_share` to `IPC$`, `smb2_share_enum_sync`, `srvsvc_NetrShareEnum_rep`, share info levels 0 and 1, share type constants, and `smb2_free_data`.

Control flow: The program parses optional `-l level`, validates level 0 or 1, parses the SMB URL, sets user when supplied, connects to `IPC$`, calls synchronous share enumeration, prints share names and optional remarks/types, frees the decoded response, and disconnects.

State and persistence behavior: It reads server share metadata only and persists nothing.

Dependencies and integration points: It validates the high-level synchronous wrapper around DCE/RPC SRVSVC share enumeration over IPC$.

Risks: Only levels 0 and 1 are supported. It exits with code 0 for invalid levels and parse failures in some branches, which can be misleading for scripts. It depends on IPC$ access and server permissions.

Test signals: Compare output against server share-listing tools. Test anonymous, authenticated, level 0, level 1, and access-denied cases.
