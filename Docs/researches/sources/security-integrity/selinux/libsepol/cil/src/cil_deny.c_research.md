# sources/security-integrity/selinux/libsepol/cil/src/cil_deny.c

## Purpose
`cil_deny.c` implements CIL deny-rule semantics. A CIL deny rule behaves like a neverallow match, but instead of reporting an error it removes matching permissions from existing allow rules. The file rewrites the AST by finding matching `allow` rules, deleting them, and inserting replacement allow rules that preserve the portions not denied.

## Important APIs, Types, And Functions
The public entry point is `cil_process_deny_rules_in_ast(struct cil_db *db)`. Public class-permission helpers exported through `cil_deny.h` are `cil_classperms_list_match_any`, `cil_classperms_list_match_all`, `cil_classperms_list_copy`, `cil_classperms_list_and`, and `cil_classperms_list_andnot`.

Internally, the file has two main layers. The permission layer recursively handles plain class permissions, map class permissions, and classpermission sets. The type-set layer uses `ebitmap_t` and `struct cil_symtab_datum` to compute intersections and differences for concrete types and type attributes. Attribute synthesis helpers such as `cil_create_attribute_d1_and_not_d2`, `cil_create_attribute_d1_and_d2`, and `cil_create_attribute_all_and_not_d` create reusable generated attributes when a result is not empty and not a single concrete type.

## Control Flow
`cil_process_deny_rules_in_ast` walks the AST, skips abstract blocks and macros, collects `CIL_DENY_RULE` nodes, and processes them in encounter order. `cil_process_deny_rule` builds a temporary `CIL_AVRULE_ALLOWED` target from the deny rule, calls `cil_find_matching_avrule_in_ast`, and for each matching allow rule calls `cil_remove_permissions_from_rule` before removing the original allow node.

`cil_remove_permissions_from_rule` first emits an allow for permissions in the original allow but not in the deny (`P1 and not P2`). It then computes common permissions (`P1 and P2`), common sources (`S1 and S2`), and non-denied sources (`S1 and not S2`). The remaining logic branches on `self`, `notself`, and `other` target pseudo-types because target matching depends on the source type. `cil_remove_permissions_from_special_rule` covers the most complicated target cases.

## State And Persistence Behavior
The file mutates the in-memory AST and symbol tables only. It inserts generated `CIL_TYPEATTRIBUTE` and `CIL_TYPEATTRIBUTESET` nodes adjacent to existing nodes, increments `db->num_types_and_attrs`, and inserts generated attributes into the local or root type symbol table. It removes original allow and deny nodes after rewriting. There is no direct disk persistence; later binary or policy serialization consumes the transformed AST.

## Dependencies And Integration Points
It depends on `cil_find.c` for matching allow rules, `cil_list` for list ownership, `cil_tree` helpers through internal headers for AST insertion/removal, `cil_symtab` for generated attributes, `cil_copy_ast` and destroy helpers for classperms ownership, `cil_strpool` for generated names, and libsepol `ebitmap` operations for set algebra. It is invoked from `cil_post_process` after initial database expansion and before final verification.

## Risks And Edge Cases
The highest-risk area is semantic equivalence of the AST rewrite, especially combinations of concrete types, attributes, `self`, `notself`, and `other`. Generated attributes must be inserted in the correct scope and must not collide with existing symbols. The code intentionally reuses existing equivalent attributes when possible; failures there can cause symbol-table growth or incorrect scope. Empty class-permission and empty type-set results are represented by NULL or empty lists, so callers must respect `cil_list_is_empty`.

## Test Signals
Useful tests compile policies with deny rules over concrete types, attributes, map classes, classpermission sets, and all special targets. Tests should compare emitted allow rules or final policydb access vectors with and without denies. Failure signals include unresolved generated attributes, duplicate names, allow rules retaining denied permissions, or denial of too broad a source/target set.
