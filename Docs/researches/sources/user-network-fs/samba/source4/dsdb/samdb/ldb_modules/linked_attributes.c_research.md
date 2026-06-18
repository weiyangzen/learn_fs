# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/linked_attributes.c

## Purpose
`linked_attributes.c` maintains consistency between forward links and backlinks in Samba's AD database. It processes add/modify operations carrying `DSDB_CONTROL_APPLY_LINKS`, updates corresponding backlink attributes after the originating operation, repairs linked DN components during rename, and defers backlink modifications until transaction prepare-commit so targets created later in the same transaction can be resolved.

## Important APIs, types, and functions
Module private state is `struct la_private`, with per-transaction `struct la_private_transaction` and a `sorted_links` feature flag. A request uses `struct la_context`, which stores schema, original request, the source object DN, pending `struct la_op_store` add/delete operations, optional replace-context state, and saved lower-operation response controls. `la_store_op()` parses link values and records target GUID plus backlink name. `la_down_req()`, `la_add_callback()`, and `la_mod_del_callback()` wrap original operations. `la_queue_mod_request()`, `la_do_mod_request()`, and `la_do_op_request()` apply deferred backlink modifications. Rename repair is handled by `linked_attributes_fix_links()`, with slow and sorted-forward-link paths.

## Control flow
Adds and modifies skip special DNs, handle `LDB_CONTROL_VERIFY_NAME_OID`, and require `DSDB_CONTROL_APPLY_LINKS`; without it, replication metadata is assumed to have handled link maintenance. The module only processes even `linkID` forward links and maps them to odd backlink attributes with `dsdb_attribute_by_linkID(linkID ^ 1)`. Adds queue backlink adds. Modifies queue backlink adds/deletes; replace and delete-without-values trigger a base search to discover old values and queue deletions before the original modify.

The original operation is sent down first. On success, pending link work is queued into transaction-private state and the original reply is completed. During `prepare_commit`, the module walks queued contexts in original order, resolves target DNs by GUID, and performs backlink add/delete modifies as system-next-module operations. Renames search the object, inspect all linked attributes, find partner objects by GUID, update old DN components to the new DN, and write modified partner link values.

## State and persistence behavior
Backlink updates are persistent DSDB modifies, but they are deferred until transaction prepare-commit. `start_transaction` allocates the per-transaction list, `prepare_commit` applies queued link operations and frees it, and `del_transaction` discards it. This design lets forward links target objects created later in the same transaction while keeping original operation replies separate from deferred maintenance failures.

## Dependencies and integration points
The module depends heavily on schema link metadata, DSDB DN parsing, GUID lookup by DN, DN lookup by GUID, sorted-link parsing helpers, `DSDB_CONTROL_APPLY_LINKS`, verify-name controls, `SAMBA_SORTED_LINKS_FEATURE`, and transaction hooks. It coordinates with `repl_meta_data.c` for replicated link changes and with `extended_dn_out.c` for runtime filtering/repair of cases backlinks cannot cover.

## Risks and edge cases
Backlink operations can fail at prepare-commit after the visible operation appeared successful, so transaction error propagation is critical. Old unsorted databases use linear scans; sorted forward links use binary-search helpers but DN+Binary values require updating all equal-GUID neighbors. Missing backlink schema definitions are tolerated for Windows 2003 compatibility. Verify-name control handling can intentionally leave critical controls to force failure when a requested GC cannot be honored. Dangling forward links on delete are tolerated in specific cases.

## Test signals
Test add/modify/replace/delete of forward links, delete-without-values, transaction ordering where target is created later, rollback/discard behavior, rename repairs for backlinks and forward links, DN+Binary duplicate-GUID cases, sorted versus unsorted feature modes, missing partner schema, verify-name behavior on GC and non-GC servers, replicated-update paths without `DSDB_CONTROL_APPLY_LINKS`, and prepare-commit failure propagation.
