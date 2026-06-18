# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_tree_connect.c

Implements SMB2 tree connect dispatch.

Key behavior:
- Decodes share path and delegates actual share connection to `smb_tree_connect()`.
- For SMB 3.1.1 non-anonymous/non-guest users, drops the connection if the request is neither signed nor encrypted.
- Encodes share type, share flags, share capabilities, and granted tree access.
- Reports encrypted-share flag when tree encryption is enabled.
- Reports DFS and continuous-availability share capabilities from tree flags.

Important dependencies:
- Core share connection: `smb_tree_connect`.
- Tree state: resource type, encryption mode, flags, access mask.

Notable details:
- Reject-unencrypted-access policy is shared with SMB1 in `smb_tree_connect_core`, not fully enforced here.
