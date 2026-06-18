# sources/security-integrity/selinux/libsepol/cil/src/cil_post.c

## Purpose
`cil_post.c` performs post-AST processing for CIL. It verifies early invariants, computes database counts and lookup arrays, evaluates attribute and expression bitmaps, builds role/user associations, evaluates classpermission and category expressions, sorts and deduplicates context rules, processes deny rules, and runs final verification.

## Important APIs, Types, And Functions
The public entry point is `cil_post_process(struct cil_db *db)`. Public sort comparators include `cil_post_filecon_compare`, `cil_post_ibpkeycon_compare`, `cil_post_portcon_compare`, `cil_post_genfscon_compare`, `cil_post_netifcon_compare`, `cil_post_ibendportcon_compare`, `cil_post_nodecon_compare`, and `cil_post_fsuse_compare`.

Key internal helpers include expression evaluation functions (`__cil_expr_to_bitmap`, `__cil_expr_list_to_bitmap`, `__evaluate_type_expression`, `__evaluate_role_expression`, `__evaluate_user_expression`, `__evaluate_permissionx_expression`, `__evaluate_cat_expression`), database walkers (`__cil_post_db_count_helper`, `__cil_post_db_array_helper`, `__cil_post_db_attr_helper`, `__cil_post_db_roletype_helper`, `__cil_post_db_userrole_helper`, `__cil_post_db_classperms_helper`, `__cil_post_db_cat_helper`), and conflict handler `__cil_post_process_context_rules`.

## Control Flow
`cil_post_process` runs `cil_pre_verify`, then `cil_post_db`, then `cil_process_deny_rules_in_ast`, then `cil_post_verify`. `cil_post_db` walks the AST multiple times. First it counts unique classes/types/attributes/roles/users and context rules. Then it fills value-to-type/role/user arrays and sort arrays. It marks neverallow-related generated attributes, evaluates attribute bitmaps and permissionx expressions, builds role-to-type and user-to-role bitmaps, evaluates classpermission and map-class expressions, evaluates MLS category expressions, and finally sorts/deduplicates each context-rule array while detecting conflicting duplicate rules.

## State And Persistence Behavior
This pass mutates `struct cil_db` and many AST payloads. It assigns numeric values to types, roles, users, categories elsewhere consumed by bitmaps; allocates `val_to_type`, `val_to_role`, `val_to_user`; allocates sorted context arrays; fills `types`, `roles`, `users`, `perms`, and category expression lists; and sets attribute `keep` flags. It performs no direct disk writes. Later binary/text emitters consume this persistent in-memory state.

## Dependencies And Integration Points
It depends on libsepol `ebitmap`, CIL verification helpers, deny processing, policy/context comparators, tree walkers, list helpers, symbol tables, and logging. It is called from `cil.c` after AST construction and before binary policy generation or textual policy output.

## Risks And Edge Cases
This is a high-blast-radius pass. Expression evaluation must correctly implement `all`, `range`, `not`, `and`, `or`, and `xor` for types, roles, users, permissions, categories, and permissionx values. Context duplicate handling depends on stable sort comparators and `db->multiple_decls`; wrong comparisons can either reject valid duplicates or silently keep conflicting labels. Attribute expansion policy is subtle: generated require/typeattr names and neverallow-only attributes are treated specially. The pass also assumes abstract blocks and macros should be skipped by most walkers.

## Test Signals
Strong tests compile full CIL policies covering type/user/role attributes, aliases, class maps, permission expressions, category ranges, MLS contexts, duplicate context rules with same and conflicting contexts, role/user associations through attributes, permissionx ranges, deny rules, and final neverallow verification. Sanitizers should watch for leaks or double frees after expression-list replacement and context-array compaction.
