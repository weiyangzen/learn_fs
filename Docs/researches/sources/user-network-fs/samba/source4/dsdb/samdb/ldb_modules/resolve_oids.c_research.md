# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/resolve_oids.c

## Purpose
`resolve_oids.c` implements the `resolve_oids` LDB module. Its job is to accept LDAP filters, requested attribute lists, add messages, and modify messages that use numeric schema OIDs for selected schema attributes, then rewrite them to Samba DSDB `lDAPDisplayName` forms before passing the request down the module stack. This mainly supports schema-related attributes where clients may refer to classes or attributes by OID but the database stores and indexes display names.

## Important APIs, Types, And Functions
The detection path is split from the mutation path. `resolve_oids_need_value()` checks whether a value looks like an OID and resolves it against the in-memory `dsdb_schema` for class-valued attributes such as `objectClass`, `subClassOf`, `auxiliaryClass`, `systemPossSuperiors`, and `possSuperiors`, or attribute-valued attributes such as `systemMustContain`, `systemMayContain`, `mustContain`, and `mayContain`. `resolve_oids_parse_tree_need()`, `resolve_oids_element_need()`, and `resolve_oids_message_need()` recursively determine whether a search tree or message requires rewriting.

`resolve_oids_replace_value()` performs the value rewrite from class `governsID` OID or attribute `attributeID` OID to the resolved `lDAPDisplayName`. `resolve_oids_parse_tree_replace()`, `resolve_oids_element_replace()`, and `resolve_oids_message_replace()` rewrite attribute names and values in shallow copies. The public module operations are `resolve_oids_search()`, `resolve_oids_add()`, and `resolve_oids_modify()`, registered by `ldb_resolve_oids_module_init()`.

## Control Flow
For search requests, the module exits early if no schema is loaded or if the base DN is special. It first scans the parse tree for OID-looking attribute names or values that the schema can resolve, then scans the requested attribute list for numeric attribute OIDs. If no rewrite is needed, the original request is passed through unchanged. Otherwise the module creates a `resolve_oids_context`, shallow-copies the parse tree and attribute list, keeps the schema alive with a talloc reference, rewrites the copied tree and attributes, builds a replacement search request, and proxies replies through `resolve_oids_callback()`.

Add and modify paths follow the same pattern: skip when no schema or special DN, scan the message for resolvable OID values, shallow-copy the message, rewrite element names and values in the copy, build a replacement add or modify request, and pass it down. Replies are forwarded as entries, referrals, or done replies without additional transformation.

## State And Persistence
The module has no persistent state. It uses request-scoped talloc allocations and references the current DSDB schema. Persistent effects happen only in lower modules after the rewritten add or modify request succeeds. The code intentionally avoids rewriting special control entries.

## Dependencies And Integration Points
This module depends on `dsdb_get_schema()`, `dsdb_attribute_by_attributeID_oid()`, `dsdb_attribute_by_lDAPDisplayName()`, `dsdb_class_by_governsID_oid()`, schema `attributeID_id` constants from DRSUAPI, LDB parse-tree structures, and LDB request builders. It is placed early in the Samba DSDB stack by `samba_dsdb.c`, before `rootdse` and schema-loading dependent modules, so later modules see canonical display-name attributes and values.

## Risks And Test Signals
The main risk is silent pass-through when an OID cannot be resolved: invalid OIDs remain unchanged and later modules decide whether to reject them. Rewriting is limited to syntax `oMSyntax == 6` and a fixed set of attribute IDs, so new schema attributes that also need OID-to-name conversion require code changes. The shallow-copy approach relies on replacement values pointing at schema-owned strings whose lifetime is protected by the talloc reference. Tests should cover search filters with OID attribute names, equality and comparison values, requested attribute OIDs, add/modify messages using class and attribute OIDs, unknown OIDs, special DNs, missing schema, and ensuring values for `governsID`, `attributeID`, and `attributeSyntax` are not incorrectly rewritten.
