# sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_enum.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_enum.c

Purpose: Demonstrates paged user account enumeration with `NetUserEnum()`.

Important APIs/types/functions: Supports levels 0, 10, 20, and 23 with `USER_INFO_*`; level 23 prints user SID via `sid_string_tos()`.

Control flow: Parses hostname and level, loops with resume handle through all pages, casts by level, prints user fields, frees buffers, and reports final error status.

State and persistence behavior: Read-only account query.

Dependencies and integration points: Verifies user create/delete/set operations and SID formatting.

Risks: Large domains depend on resume progress. Level selection controls sensitive field exposure.

Test signals: Enumerate at all supported levels before/after disposable user creation.
