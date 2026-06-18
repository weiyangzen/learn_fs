# sources/security-integrity/selinux/libsepol/cil/src/cil_verify.c

## Purpose

`cil_verify.c` performs syntax and semantic checks that complement AST building and resolution. It validates identifier names, expression syntax, constraint expression legality, conditional blocks, macro parameter shadowing, self-referential attributes, ordered-list completeness, MLS ranges, users/roles/types/bounds, contexts, booleanif contents, extended permissions, class/common permission collisions, map-class classpermissions, and selected policy-global uniqueness.

## Important APIs, Types, and Functions

Public helpers include `cil_verify_name()`, `__cil_verify_syntax()`, `cil_verify_expr_syntax()`, `cil_verify_constraint_leaf_expr_syntax()`, `cil_verify_constraint_expr_syntax()`, `cil_verify_conditional_blocks()`, `cil_verify_decl_does_not_shadow_macro_parameter()`, `__cil_verify_ranges()`, `cil_verify_completed_ordered_list()`, `__cil_verify_ordered()`, `__cil_verify_initsids()`, `__cil_verify_senscat()`, `__cil_verify_helper()`, and `__cil_pre_verify_helper()`. Internal helpers cover reserved names, no-self-reference recursion, MLS/category checks, pre/post user validation, role/type circular bounds, context validity, booleanif subtree validation, per-context statement checks, permissionx verification, class verification, policycap lookup, and classpermission/map-class recursion.

## Control Flow

Name verification checks null, length, first character, allowed characters depending on `db->qualified_names`, and flavor-specific reserved words. Syntax verification walks parse sibling nodes against `enum cil_syntax` masks, including variadic list/string tails. Constraint and expression syntax layer operator-specific shape rules on top.

Pre-verification (`__cil_pre_verify_helper`) skips macros and abstract blocks, checks users before evaluation, validates map classes and classpermissions, and uses `cil_stack` to detect self-reference in user/role/type attributes and catsets. Main verification (`__cil_verify_helper`) runs in two pass values: pass 0 validates post-evaluation users, roles, types, singleton `handleunknown`/`mls`, booleanifs, named ranges, classes, and policycaps; pass 1 validates contexts and context-bearing statements plus extended permissions. Booleanif validation recursively walks condblocks and rejects neverallow, deny rules, and disallowed statement flavors.

Classpermission verification recursively follows classpermissionsets and map permissions, using a tortoise-style step/limit cycle detection to catch circular class permission definitions. MLS verification ensures sensitivity dominance, low categories are a subset of high categories, and categories are allowed for their sensitivities.

## State and Persistence Behavior

Most verification is read-only, but it writes output counters through `cil_args_verify`: `handleunknown`, `mls`, and `nseuserdflt`. It also uses temporary stacks and lists. Some checks inspect resolved bitmaps (`user->roles`, `role->types`), ordered lists on `db`, resolved class/common permission symtabs, and `datum_expr` lists produced by the resolver.

## Dependencies and Integration Points

The verifier depends on libsepol policy capability lookup, ebitmap access through CIL internals, CIL tree/list/stack utilities, resolver-produced datums and ordered lists, `cil_find`/class expansion for permissionx checks, and logging. It is run after resolution phases and before policy database emission.

## Risks and Edge Cases

Several checks rely on pointer identity for interned keywords and resolved datums. Context validation assumes users have ranges and roles, roles have types, and ranges are resolved. The commented-out duplicate rule verification shows a known gap for type/role rule duplicate checking. Booleanif validation has policy-version-specific allowance for extended avrules. `__cil_verify_levelrange_cats()` has a redundant condition but effectively accepts a null low category set. Classpermission recursion must handle `all`, nested lists, map permissions, empty lists, and cycles.

## Test Signals

Tests should cover invalid names and reserved words by flavor, expression arity/operator errors, constraint operand restrictions, duplicate true/false conditional blocks, macro parameter shadowing, attribute self-reference cycles, incomplete ordered declarations, circular user/role/type bounds, invalid context user-role-type-range combinations, named and anonymous range validation, invalid netif/file/node/device contexts, permissionx classes without ioctl/nlmsg permissions, class/common duplicate permissions, circular classpermissionsets, and booleanif disallowed statements.
