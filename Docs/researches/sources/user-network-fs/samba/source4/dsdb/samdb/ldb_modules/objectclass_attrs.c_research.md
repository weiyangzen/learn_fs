# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/objectclass_attrs.c

## Purpose
`objectclass_attrs.c` validates entry attributes against schema and objectClass constraints. It checks that attributes exist, values match syntax, constructed/backlink/system-only attributes are not illegally written, names and values are normalized, delete-protected attributes remain present, required attributes exist, and schema attribute definitions are loadable before persistence is accepted.

## Important APIs, types, and functions
`struct oc_context` carries module/request/schema, a copied request message, the post-operation search result, and saved lower reply. `oc_validate_dsheuristics()` implements special string-position constraints. `oc_auto_normalise()` canonicalizes values using the syntax handler. `attr_handler()` performs pre-operation attribute validation and sends a copied add/modify. `oc_op_callback()` runs after the lower operation, searches the stored entry, and calls `attr_handler2()` for full objectClass allow/must validation. Module handlers are `objectclass_attrs_add()` and `objectclass_attrs_modify()`.

## Control flow
Adds and modifies bypass special DNs and no-schema cases. Modify with `DSDB_CONTROL_SEC_DESC_PROPAGATION_OID` is allowed only for a single `nTSecurityDescriptor` change and then bypasses the rest. Otherwise `attr_handler()` copies the request message, checks each element against schema, allows dbcheck to remove unknown attributes on modify, rejects direct backlink modification without relax/dbcheck, enforces systemOnly constraints with documented exceptions, validates syntax unless internal disable-validation is set or dbcheck is present, rejects constructed attributes, validates `dSHeuristics`, auto-normalizes values, and fixes attribute-name case.

After the lower add/modify returns done, `oc_op_callback()` searches the actual object with `nTSecurityDescriptor` and `*`, including show-recycled and reveal-internals controls. `attr_handler2()` reads final objectClass, blocks untrusted LDAP creation/change of `secret` and `trustedDomain`, builds full MUST/MAY attribute lists, enforces a hardcoded delete-protected attribute list when those attributes were part of the request, rejects attributes not allowed by the object's classes except harmless `parentGUID` and dbcheck repair cases, verifies replicated mandatory attributes are present unless the object is deleted, and validates new `attributeSchema` objects can be translated to `struct dsdb_attribute` with a known syntax.

## State and persistence behavior
The module has no durable private state. It validates by first letting the lower operation occur, then reading the resulting object and only completing the original request if final constraints pass. In a transactional LDB stack, a failure after lower modify should abort the operation.

## Dependencies and integration points
It depends on schema attributes and syntax handlers, DSDB full attribute list helpers, dbcheck/relax/restore tombstone/security descriptor propagation controls, system access checks, and objectClass sorting/defaulting performed by `objectclass.c` earlier in the stack.

## Risks and edge cases
Because full validation happens after lower persistence, correct transaction rollback is essential. SystemOnly rules have many exceptions and use schema-base comparison plus system access as a proxy for some AD upgrade states. Dbcheck bypasses are intentionally broad enough to repair broken entries but must not leak into normal LDAP writes. Constructed attributes return different LDAP errors on add versus modify.

## Test signals
Test unknown attributes, invalid syntax, auto-normalization, direct backlink modification, systemOnly writes with relax/dbcheck/restore/system access, constructed attributes on add/modify, `dSHeuristics` positional constraints, security descriptor propagation bypass, delete-protected attributes, missing mandatory attributes on live versus deleted objects, untrusted LSA objectclass rejection, schema attribute translation failures, and dbcheck repair allowances.
