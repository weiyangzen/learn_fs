# sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_dispinfo.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_dispinfo.c

Purpose: Demonstrates display-oriented user enumeration through `NetQueryDisplayInformation()`.

Important APIs/types/functions: Uses level 1 and `NET_DISPLAY_USER`, index paging, preferred length, and returned entry counts.

Control flow: Parses hostname, repeatedly queries display information starting at an index, prints user name/full name/comment/flags-style fields, frees each page, and advances by entries read until completion.

State and persistence behavior: Read-only directory/account query.

Dependencies and integration points: Alternative to `NetUserEnum()` for UI-style user lists.

Risks: Paging is index-based and must avoid infinite loops if server returns no progress. Only user display level is covered.

Test signals: Compare output with `user_enum` for known accounts and exercise multi-page results.
