# sources/security-integrity/selinux/libsepol/src/policydb_validate.c

## Purpose
`policydb_validate.c` is the structural integrity pass for an in-memory `policydb_t`. It rejects malformed or internally inconsistent policy databases before they are trusted by serialization, expansion, or service APIs. It covers both kernel policies and base/module policies and validates version-dependent structures such as conditionals, filename transitions, policy capabilities, permissive/neveraudit maps, range transitions, and type/attribute maps.

## Important APIs, Types, and Functions
The exported functions are `value_isvalid()` and `policydb_validate()`. Internal validation state is carried by `validate_t`, which records a symbol table's primitive count and an ebitmap of value gaps derived from `*_val_to_name` arrays. `map_arg_t` packages validation flavors with a handle and policy for hash callbacks, while `perm_arg_t` detects duplicated or inherited permission values.

Major helpers validate primitive values and ebitmaps, symbol datums, access-vector tables, conditional expressions, avrules, role transition/allow lists, filename transitions, contexts, object contexts, genfs entries, module declaration scopes, permissive/neveraudit maps, range transitions, and kernel type/attribute maps.

## Control Flow
`policydb_validate()` initializes all validation flavors, checks global policy properties and policy capabilities, then branches by `policy_type`. Kernel policies validate the TE avtab, conditionals, role transitions/allows, and filename transitions. Base/module policies validate avrule blocks, declarations, scope indices, and declaration-local symbol tables. Both paths then validate ocontexts, genfs, scopes, datum array gaps and entries, permissive/neveraudit maps, range transitions, and attr maps. Any failure logs through `ERR(handle, ...)`, destroys temporary gap ebitmaps, and returns `-1`.

## State and Persistence
The file does not persist policy state. It allocates temporary gap ebitmaps and otherwise reads linked lists, hashtabs, reverse lookup arrays, ebitmaps, and context structs in place. Gap handling is version-aware for older kernel policy versions where attributes can appear only in `type_attr_map`.

## Dependencies and Integration
It depends on policydb core types, ebitmap operations, conditional policy, policy capability names, target-platform constants, and feature helpers such as `policydb_has_cond_xperms_feature()`. It is an integrity gate for read/write and service paths.

## Risks and Test Signals
The code is sensitive to one-based policy values versus zero-based arrays. Constraint and conditional expressions are checked as bounded stack programs. Extended permissions are SELinux-only and version-gated. Good tests corrupt symbol gaps, invalid bounds, malformed RPN, unsupported xperms, bad ocontext ranges, and module scope indices, then assert validation failure.
