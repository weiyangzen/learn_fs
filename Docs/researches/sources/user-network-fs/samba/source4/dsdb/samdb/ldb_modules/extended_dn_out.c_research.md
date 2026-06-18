# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/extended_dn_out.c

## Purpose
`extended_dn_out.c` is an LDB search-response module that turns Samba DSDB storage DNs into client-visible DNs. It optionally injects `<GUID=...>` and `<SID=...>` components into returned object DNs, normalizes DN/RDN and attribute-name case, rewrites DN-valued attributes, and hides deleted or internal link values unless the caller has reveal-style controls. It is the output-side companion to `extended_dn_store.c`.

## Important APIs, types, and functions
The module private state is `struct extended_dn_out_private`, holding `dereference`, `normalise`, and `attrs`; only `normalise` and the store-format opaque are materially used in this file. `struct extended_search_context` carries the request, schema, injection flags, attribute-removal flags, and requested extended-DN type.

Key helpers are `copy_attrs()` and `add_attrs()` for safely extending a requested attribute list, `inject_extended_dn_out()` for setting `GUID` and optional `SID` extended components on `ares->message->dn`, and `fix_one_way_link()` for resolving one-way DN links by GUID so renamed targets are returned with current DN components. The main callback is `extended_callback()`, installed by `extended_dn_out_search()`. Module registration exports `ldb_extended_dn_out_module_init()` with ops named `extended_dn_out_ldb`.

## Control flow
`extended_dn_out_ldb_search()` calls `extended_dn_out_search()`. Special DNs bypass the module. The search path inspects `LDB_CONTROL_EXTENDED_DN_OID` and `DSDB_CONTROL_DN_STORAGE_FORMAT_OID`; if either requires extended output it records the requested `struct ldb_extended_dn_control` type and ensures `objectGUID` and possibly `objectSid` are requested from lower modules even if the client did not ask for them. Those temporary attributes are removed after DN injection.

`extended_callback()` forwards referrals and done replies, then processes each entry. It optionally normalizes the entry DN, injects GUID/SID, regenerates `distinguishedName`, and walks every schema-known DN-valued attribute. Deleted linked values and hidden backlinks are skipped unless reveal controls apply. DN values are parsed via `dsdb_dn_parse_trusted()`, one-way links are resolved by GUID, internal extended components are filtered to GUID/SID for ordinary callers, and values are replaced with either extended or plain linearized forms.

## State and persistence behavior
This module does not persist changes. It mutates transient reply messages and DN value blobs before forwarding them to the original request callback. Its only lasting process state is an LDB opaque, `DSDB_EXTENDED_DN_STORE_FORMAT_OPAQUE_NAME`, set during init to advertise that DNs are stored in extended form.

## Dependencies and integration points
The module depends on DSDB schema lookup, DN parsing and rendering helpers, `dsdb_fix_dn_rdncase()`, GUID/SID extended component helpers, and internal DSDB search flags such as `DSDB_SEARCH_SHOW_DELETED`, `DSDB_SEARCH_SHOW_RECYCLED`, and `DSDB_SEARCH_SHOW_DN_IN_STORAGE_FORMAT`. It registers `LDB_CONTROL_EXTENDED_DN_OID` with rootDSE and consumes reveal/storage-format controls. It integrates closely with linked-attribute handling, because it filters deleted/hidden link metadata and repairs one-way links for display.

## Risks and edge cases
Injection requires `objectGUID`; failure to extend the lower search attribute list causes an operations error. DN-valued attributes with invalid syntax abort the whole search with `LDB_ERR_INVALID_DN_SYNTAX`. One-way link repair may issue per-value searches across all partitions, so large result sets with many one-way links can be expensive. Filtering hidden backlinks depends on whether the caller explicitly requested the backlink attribute. Reveal controls intentionally expose otherwise hidden deleted/internal values for dbcheck-style repair paths.

## Test signals
Useful tests include searches with and without `LDB_CONTROL_EXTENDED_DN_OID`, searches requesting explicit attribute lists that omit `objectGUID`/`objectSid`, `distinguishedName` regeneration, hidden backlink filtering, deleted linked-value filtering with and without reveal controls, one-way link rename repair, invalid DN-valued attribute handling, and storage-format searches used by linked-attribute maintenance.
