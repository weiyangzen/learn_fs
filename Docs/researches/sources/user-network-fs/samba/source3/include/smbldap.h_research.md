# sources/user-network-fs/samba/source3/include/smbldap.h

## Purpose
`smbldap.h` declares Samba's traditional LDAP helper API, guarded by `HAVE_LDAP`. It wraps LDAP connection setup, bind callbacks, modification-list construction, attribute extraction, searches, TLS startup, and talloc-based cleanup helpers around the platform LDAP library.

## Important APIs, Types, and Functions
- State and callback: opaque `struct smbldap_state` and `smbldap_bind_callback_fn`.
- Connection lifecycle: `smbldap_init`, `smbldap_get_ldap`, `smbldap_setup_full_conn`, `smbldap_start_tls`, and `smbldap_start_tls_start`.
- Paging and binding: `smbldap_get_paged_results`, `smbldap_set_paged_results`, and `smbldap_set_bind_callback`.
- Modification helpers: `smbldap_set_mod`, `smbldap_set_mod_blob`, `smbldap_make_mod`, and `smbldap_make_mod_blob`.
- LDAP operations: `smbldap_search` and `smbldap_modify`.
- Attribute extraction: `smbldap_get_single_attribute`, `smbldap_talloc_single_attribute`, `smbldap_talloc_first_attribute`, `smbldap_talloc_smallest_attribute`, `smbldap_talloc_single_blob`, `smbldap_pull_sid`, and `smbldap_talloc_dn`.
- Cleanup helpers: `smbldap_talloc_autofree_ldapmsg` and `smbldap_talloc_autofree_ldapmod`.

## Control Flow and State
The main state object owns an LDAP connection plus Samba-specific settings such as paged-result preference and optional bind callback. Callers initialize the state, optionally configure callbacks/paging, perform searches/modifies, and rely on talloc cleanup helpers to release LDAP result and mod arrays.

## Persistence Behavior
Search helpers are read-only against directory state, while `smbldap_modify` and password/TLS-related downstream operations can mutate LDAP directory entries. This header itself only declares the persistence boundary.

## Dependencies and Integration Points
It includes `include/smb_ldap.h`, `talloc.h`, and `tevent.h` when LDAP is enabled. It integrates with passdb/ldapsam, account management, SID/GUID conversion, and any source3 code that still uses the synchronous LDAP API rather than `tldap`.

## Risks
- Every declaration is hidden when `HAVE_LDAP` is false; callers must guard use correctly.
- LDAPMod array ownership is subtle and depends on the talloc autofree wrappers.
- Attribute extraction APIs need clear handling of missing, multi-valued, binary, or oversized attributes.
- TLS startup split between `_start` and synchronous variants can be misused if the connection state is assumed secure too early.

## Test Signals
LDAP-enabled build coverage, ldapsam account tests, TLS bind tests, paged-result searches, binary SID/blob extraction tests, and leak checks around LDAPMessage/LDAPMod cleanup provide useful signals.
