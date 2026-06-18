<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tldap_util.c -->
# sources/user-network-fs/samba/source3/lib/tldap_util.c

## Purpose
`tldap_util.c` supplies convenience helpers around the core tldap client: attribute extraction, SID/GUID/integer conversion, LDAP modify-list construction, formatted search wrappers, rootDSE fetching/caching, control helpers, and RFC2696 paged searches.

## Important APIs, types, and functions
Attribute readers include `tldap_entry_values`, `tldap_get_single_valueblob`, `tldap_talloc_single_attribute`, `tldap_pull_binsid`, `tldap_pull_guid`, `tldap_pull_uint64`, and `tldap_pull_uint32`. Modification builders include `tldap_add_mod_blobs`, `tldap_add_mod_str`, `tldap_make_mod_blob`, and `tldap_make_mod_fmt`. Search utilities include `tldap_search_va`, `tldap_search_fmt`, `tldap_fetch_rootdse[_send/_recv]`, `tldap_rootdse`, `tldap_supports_control`, `tldap_add_control`, `tldap_msg_findcontrol`, and paged search send/recv helpers.

## Control flow
Attribute helpers lazily force `tldap_entry_attributes` parsing and then scan values by case-insensitive attribute name. Modify helpers compare existing single-valued attributes with intended values, deleting the old value before adding the new value to avoid LDAP servers rejecting same-value delete/add pairs. RootDSE fetch performs a base search on `""` with `*` and `+`, requires exactly one entry before the final result, validates DN parsing, and stores the message as context attribute `tldap:rootdse`. Paged search appends a paged-results control, ships a normal search, forwards intermediate entries to callers, then decodes the returned cookie and issues the next page until the cookie is empty.

## State and persistence behavior
RootDSE is cached on the tldap context. Paged search state owns the current cookie, temporary ASN.1 control blob, current result message, and copied server controls. Modify construction allocates talloc-owned arrays under caller-provided memory contexts.

## Dependencies and integration points
The file depends on `tldap.c`, Samba charset conversion, SID/GUID parsing, ASN.1 helpers, `smb_strtoull`, and LDAP paged-results OID constants. Higher-level directory code uses it to build safe modifications and discover server controls.

## Risks and edge cases
`tldap_add_mod_blobs` increments `*pnum_mods` even when appending values to an existing mod, which callers must understand. Multi-valued attributes are not modified by `tldap_make_mod_blob_int`. UTF-8 comparison treats conversion failure as equality, avoiding churn but potentially hiding invalid data. Paged search requires the server to return the paged-results control and treats absence as protocol error.

## Test signals
Targeted tests should cover single and multi-value extraction, SID/GUID decoding, no-op modify detection, rootDSE protocol validation, paged search cookie continuation, and missing paged-results control handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tldap_util.c -->
