# sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_enum.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_enum.c

Purpose: Demonstrates paged local group enumeration with `NetLocalGroupEnum()`.

Important APIs/types/functions: Supports levels 0 and 1 using `LOCALGROUP_INFO_0` and `_1`, with resume-handle paging.

Control flow: Parses hostname and optional level, loops on success or `ERROR_MORE_DATA`, prints group names and optional comments, frees each page, and handles final status.

State and persistence behavior: Read-only remote local group query.

Dependencies and integration points: Verifies create/delete/setinfo local group examples.

Risks: Only two levels are interpreted. Large result sets depend on resume behavior.

Test signals: Enumerate before and after creating a test local group and force small preferred lengths if supported.
