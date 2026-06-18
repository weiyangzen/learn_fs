# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/ranged_results.c

## Purpose

`ranged_results.c` implements the `ranged_results` LDB module. It supports Active Directory-style ranged attribute retrieval requests such as `member;range=0-1499` by asking lower modules for the full base attribute and then slicing the returned values before sending results to the client. This allows clients to request windows of a multi-valued attribute even when lower storage modules do not natively implement ranged result syntax.

## Important APIs, Types, And Functions

`struct rr_context` stores the original module/request and whether a dirsync control is present. Dirsync changes behavior because dirsync incremental-value handling interacts with ranged results.

Key functions:

- `rr_init_context()` allocates request context and records whether `LDB_CONTROL_DIRSYNC_OID` is present.
- `rr_search()` scans requested attributes for `;range=`, validates syntax, strips range suffixes into a new attribute list, and sends a rewritten downstream search.
- `rr_search_callback()` receives downstream replies, slices matching attributes for each entry, renames the returned attribute with the appropriate `;range=start-end` or `;range=start-*` suffix, and forwards entries/referrals/done replies.
- `ldb_ranged_results_module_init()` registers the module with `.search = rr_search`.

## Control Flow

`rr_search()` is invoked for search operations. It iterates over `req->op.search.attrs`, looking for the first semicolon in each attribute and accepting only `;range=` at that point. It parses either `start-*` or `start-end`. Malformed ranges and `start > end` return `LDB_ERR_UNWILLING_TO_PERFORM`. For each range request, it replaces the attribute name in `new_attrs` with the base attribute before the semicolon, preserving other attributes unchanged. If at least one ranged request was found, it builds a downstream search with the same base, scope, filter, controls, and stripped attribute list; otherwise it frees the temporary array and passes the original request onward.

`rr_search_callback()` passes referrals and done replies through. If dirsync is in use, it forwards entries without slicing because dirsync and ranged results have special interaction. Otherwise it loops over the original requested attributes, reparses range syntax, finds the base attribute in the returned message, computes the effective end index, copies only requested values into a newly allocated value array, and renames the attribute. If requested end reaches or exceeds the last available value, the returned name ends in `*`; if `start` is beyond the last available value, it returns the ranged attribute with zero values.

## State And Persistence Behavior

The module has no persistent storage. All state is per search request and owned by talloc contexts tied to the original request or reply message. It mutates the in-flight `ares->message` before forwarding it: `el->values`, `el->num_values`, and `el->name` are replaced for ranged attributes. It does not alter the underlying database.

## Dependencies And Integration Points

The module depends on LDB module APIs, talloc allocation, and `LDB_CONTROL_DIRSYNC_OID`. It is in the main Samba DSDB module stack before modules such as ANR/sort/asq according to `samba_dsdb.c`. The dirsync module marks or uses range-like attributes and comments that ranged_results must know how to behave when dirsync is active.

Client-visible integration is LDAP/AD ranged retrieval syntax. `source4/dsdb/tests/python/ldap.py` contains direct tests for `servicePrincipalName;range=0-*`, fixed ranges, beyond-end ranges returning `*`, and empty ranges past the end. `source4/dsdb/tests/python/dirsync.py` includes dirsync/range interaction cases for `member;range=...`.

## Risks And Edge Cases

The module assumes that a returned attribute's value order is suitable for slicing and that the full base attribute can be fetched before slicing, which can be expensive for very large attributes. It only checks for the first semicolon and requires `;range=` immediately there, so attributes with other options before range are ignored or passed through. It allocates a new values array sized `(end - start) + 1`; while it checks overflow for `start + end`, the size expression still depends on parsed unsigned arithmetic and effective end normalization.

The entry callback assumes `ac->req->op.search.attrs` is non-NULL when a range was found in `rr_search()`, which is valid for rewritten range requests but is a contract to preserve. Dirsync bypass returns full values when `dirsync_in_use`; changes in dirsync semantics could require revisiting this behavior. Returned values are shallow-copied `struct ldb_val`s from the original array, so lifetime must remain tied to the reply message, which is true in the current callback flow.

## Test Signals

Primary regression signals are the LDAP Python tests around `servicePrincipalName;range=...` and the dirsync Python tests around `member;range=...` with incremental values. Unit or integration tests should cover malformed ranges, `start > end`, `start-*`, exact last-value requests, request end beyond last value, start beyond last value, multiple ranged attributes in one request, mixed ranged and normal attributes, no attrs list, and dirsync control presence. Build registration is covered by the `ldb_ranged_results` module entry in `wscript_build_server`.
