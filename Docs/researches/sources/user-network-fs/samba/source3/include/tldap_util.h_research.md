# sources/user-network-fs/samba/source3/include/tldap_util.h

## Purpose
`tldap_util.h` declares convenience helpers layered on top of `tldap.h` for attribute extraction, typed conversion, modification-list construction, formatted searches, RootDSE fetching, control handling, and paged searches.

## Important APIs, Types, and Functions
- Attribute/value extraction: `tldap_entry_values`, `tldap_get_single_valueblob`, `tldap_talloc_single_attribute`, `tldap_pull_binsid`, `tldap_pull_guid`, `tldap_pull_uint64`, and `tldap_pull_uint32`.
- Modification builders: `tldap_add_mod_blobs`, `tldap_add_mod_str`, `tldap_make_mod_blob`, and `tldap_make_mod_fmt`.
- Error/search helpers: `tldap_errstr`, `tldap_search_va`, and `tldap_search_fmt`.
- RootDSE: `tldap_fetch_rootdse_send`, `tldap_fetch_rootdse_recv`, `tldap_fetch_rootdse`, and `tldap_rootdse`.
- Controls: `tldap_entry_has_attrvalue`, `tldap_supports_control`, `tldap_add_control`, and `tldap_msg_findcontrol`.
- Paged search: `tldap_search_paged_send` and `tldap_search_paged_recv`.

## Control Flow and State
The helpers either synchronously inspect a `tldap_message`, append to talloc-owned arrays, or wrap async LDAP operations. Paged searches build on repeated search requests and controls, returning messages through the request/recv pattern. RootDSE fetch caches or exposes RootDSE information through the LDAP context.

## Persistence Behavior
Read helpers do not persist state. Modification builders produce request data consumed by LDAP modify/add calls, which may persist directory changes. RootDSE state may be cached in the `tldap_context` implementation.

## Dependencies and Integration Points
It includes `includes.h`, so it expects the broader Samba source3 context. It integrates with `tldap.h`, SID/GUID parsing, directory capability discovery, and code that needs formatted filters or paged results.

## Risks
- Formatted search helpers must escape LDAP filter input correctly in their implementations; the declaration marks printf attributes for compiler checking.
- Attribute conversion helpers need robust handling of missing, duplicated, malformed, and endian-sensitive values.
- Paged-search control handling must avoid infinite loops and must handle servers that omit or reject the control.

## Test Signals
Tests should cover attribute extraction edge cases, SID/GUID/integer parsing, formatted filter generation, RootDSE control discovery, paged search continuation/end behavior, and memory ownership of generated mod arrays.
