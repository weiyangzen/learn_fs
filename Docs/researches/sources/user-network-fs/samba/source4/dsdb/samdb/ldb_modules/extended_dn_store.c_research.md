# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/extended_dn_store.c

## Purpose
`extended_dn_store.c` is the input-side extended-DN module. On add and modify operations, it finds DN-valued attributes, resolves each referenced object, and rewrites values into Samba's storage format containing GUID/SID metadata. It also implements foreign-security-principal handling for FPO-enabled attributes, allowing an input like `<SID=...>` to create or resolve a `foreignSecurityPrincipal` when policy permits.

## Important APIs, types, and functions
`struct extended_dn_context` tracks schema, module, original and rewritten requests, a linked list of pending DN replacement operations, and a cached trust routing table. Each pending replacement is `struct extended_dn_replace_list`, holding the parsed `dsdb_dn`, the value pointer to rewrite, a base search request, `fpo_enabled`, `require_object`, and `got_entry` flags.

`extended_dn_context_init()` creates request state. `extended_store_replace()` parses a DN value, decides whether the target must exist, builds a base search with `DSDB_SEARCH_SHOW_DN_IN_STORAGE_FORMAT`, and queues the operation. `extended_replace_callback()` drives the queue, rewriting values through `extended_replace_dn()` and finally issuing the rewritten add/modify request. `extended_dn_handle_fpo_attr()` implements the foreign SID path. Public module entry points are `extended_dn_add()`, `extended_dn_modify()`, and `ldb_extended_dn_store_module_init()`.

## Control flow
Adds and modifies bypass special DNs and no-schema cases. The module scans each message element; schema attributes that are not DN-valued or are `distinguishedName` are ignored. On the first relevant value, the request message is shallow-copied and a replacement add/modify request is built with `extended_final_callback()` to relay the final reply.

For each DN value, `extended_store_replace()` parses it with the attribute syntax OID. Self-references during add are skipped because the object cannot be found yet. Non-extended delete values are skipped because the delete already carries enough information. Otherwise a base search is queued to resolve the target into storage format. `extended_replace_callback()` processes each search in order. If the target is missing and required, it returns `WERR_DS_NAME_REFERENCE_INVALID`; if the target is optional, it clears the lower-layer error and proceeds. Once all values are processed, the copied request is sent down.

## State and persistence behavior
The module itself stores no durable state, but it rewrites inbound operations that will become persistent directory values. It may also persist a new `foreignSecurityPrincipal` object as system before rewriting the attribute value to the newly created DN. Its in-flight state is talloc-owned by the request.

## Dependencies and integration points
The code relies on DSDB schema metadata, `dsdb_dn_parse()`, `dsdb_dn_construct()`, `dsdb_module_search_dn()`, `dsdb_module_add()`, trust routing helpers, domain SID helpers, and controls such as `DSDB_CONTROL_DBCHECK_FIX_DUPLICATE_LINKS`, `DSDB_CONTROL_DBCHECK_FIX_LINK_DN_SID`, `LDB_CONTROL_RELAX_OID`, and `DSDB_CONTROL_DBCHECK`. FPO-enabled attributes are recognized by DRSUAPI ATTIDs for `member`, `msDS-MembersForAzRole`, `msDS-NeverRevealGroup`, and `msDS-RevealOnDemandGroup`; `msDS-NonMembers` is explicitly rejected.

## Risks and edge cases
Incorrect required-object decisions can either reject legal provisioning/dbcheck repairs or allow dangling links. FPO creation is security-sensitive: local-domain, BUILTIN, within-forest, and unsupported SID cases have distinct Windows-compatible errors. Request rewriting mutates copied values by pointer, so lifetime and talloc ownership are important. The module intentionally bypasses dbcheck duplicate-link/fix-SID controls to avoid interfering with repair operations.

## Test signals
Test normal add/modify of DN-valued attributes, deletion of DN values with and without extended components, missing targets under trusted/untrusted/relax/dbcheck contexts, self-references on add, FPO-enabled foreign SID creation, rejection of local/BUILTIN/within-forest missing SIDs, unsupported `msDS-NonMembers`, and coexistence with dbcheck link-fix controls.
