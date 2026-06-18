# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/objectclass.c

## Purpose
`objectclass.c` enforces objectClass hierarchy, naming, parent-child constraints, DN normalization, objectCategory defaults, selected systemFlags rules, structural-class immutability, rename constraints, and delete protections. It is one of the central AD semantics modules for add, modify, rename, and delete operations.

## Important APIs, types, and functions
`struct oc_context` carries module/request/schema state, one or two search replies, and a continuation `step_fn`. `oc_init_context()` initializes it. `check_unrelated_objectclasses()` rejects unsatisfied abstract classes or disjoint structural class combinations. `get_search_callback()` is the common async search continuation. `fix_dn()` normalizes child DN components against the parent DN.

Operation paths are `objectclass_add()` / `objectclass_do_add()`, `objectclass_modify()` / `oc_modify_callback()` / `objectclass_do_mod()`, `objectclass_rename()` / `objectclass_do_rename()` / `objectclass_do_rename2()`, and `objectclass_delete()` / `objectclass_do_delete()`. Init registers `LDB_CONTROL_RODC_DCPROMO_OID` and stores the extended-DN store-format opaque.

## Control flow
Adds bypass special DNs and reject base-DN re-adds without NC-head `instanceType` by returning an LDAP referral. For normal children, the module searches the parent with show-recycled/system controls, normalizes the new DN, requires objectClass, sorts the class list, finds the structural class, validates RDN attribute compatibility, rejects system-only classes unless relax or special RODC DCPROMO applies, checks parent `systemPossibleInferiors`, validates or defaults `objectCategory`, applies default hiding and systemFlags rules, rejects direct `isCriticalSystemObject`, and forwards a rewritten add.

Modify first strips non-objectClass changes into a lower modify. If objectClass changes are present, older forest functional levels reject changes under standard NCs. After non-class changes succeed, it searches the stored objectClass, applies requested objectClass add/replace/delete semantics, resorts the list, ensures the structural class is unchanged, checks unrelated classes, and sends a final replace of objectClass.

Rename searches the new parent and old object, bypassing dbcheck. It validates RDN compatibility, allowed parent class, and prevents moving an object below itself. It then normalizes the new DN and forwards a rewritten rename. Delete searches the object unless relax is present and blocks deletion of this DC's nTDSDSA, this DC's RID Set, deleted objects by untrusted/non-system callers, protected crossRefs, objects with `SYSTEM_FLAG_DISALLOW_DELETE`, and critical system objects during tree-delete except selected SAM classes.

## State and persistence behavior
The module rewrites requests but stores no module-private durable data. Its persistent effects are normalized DNs, defaulted `objectCategory`, `showInAdvancedViewOnly`, and `systemFlags` on adds, and validated objectClass replacements on modifies.

## Dependencies and integration points
It depends on DSDB schema class metadata, possible inferior lists, objectCategory defaults, functional-level helpers, default/config/schema base DNs, system access controls, RODC DCPROMO control registration, and extended-DN storage format choices. It runs in concert with `objectclass_attrs.c`, which validates attribute allow/must lists after the operation.

## Risks and edge cases
AD compatibility rules are dense and order-sensitive. Parent searches include recycled objects to support DRS delete flows. The structural class pointer comparison assumes classes come from the same schema instance. SystemFlags behavior is intentionally class-specific and may miss obscure Windows rules. Rename/delete protection bypasses for dbcheck/relax are necessary but security-sensitive.

## Test signals
Test add with missing objectClass, invalid RDN, invalid parent class, system-only class with and without relax/RODC control, objectCategory default/validation under both extended-DN storage modes, systemFlags masks for schema/site/server/linkID cases, objectClass modify add/delete/replace with structural-class immutability, forest-level restrictions, rename parent/RDN/self-child checks, and delete protections for nTDSDSA, RID Set, crossRef, deleted objects, disallow-delete, and critical tree-delete.
