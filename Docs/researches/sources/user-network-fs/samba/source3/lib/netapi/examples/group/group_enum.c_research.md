# sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_enum.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_enum.c

Purpose: Demonstrates paged enumeration of global/domain groups with `NetGroupEnum()`.

Important APIs/types/functions: Supports levels 0, 1, 2, and 3 using `GROUP_INFO_0/1/2/3`; level 3 converts group SIDs with `sid_string_tos()`.

Control flow: Parses hostname and optional level, loops on success or `ERROR_MORE_DATA`, casts returned buffers by level, prints group name/comment/rid/SID/attributes, frees each page, and advances resume state.

State and persistence behavior: Read-only query. Resume handle tracks enumeration position.

Dependencies and integration points: Uses NetAPI buffer allocation rules and SID formatting from Samba headers.

Risks: Printing assumes level-specific structures match server response. Large domains rely on correct resume handling.

Test signals: Enumerate at each supported level against a test domain and compare counts with known group inventory.
