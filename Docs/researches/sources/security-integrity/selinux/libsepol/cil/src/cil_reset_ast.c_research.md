# sources/security-integrity/selinux/libsepol/cil/src/cil_reset_ast.c

## Purpose

`cil_reset_ast.c` clears resolution-time state from a CIL AST so the same tree can be re-resolved after optional blocks are disabled or declarations are otherwise invalidated. It deliberately preserves parse/build-time strings and structural AST nodes while nulling resolved pointers, destroying derived datum-expression lists, clearing ordering flags, and undoing class/common permission value shifts.

## Important APIs, Types, and Functions

The public API is `cil_reset_ast(struct cil_tree_node *current)`, which walks a subtree with `cil_tree_walk()` and dispatches by `node->flavor` in `__cil_reset_node()`. The file contains many flavor-specific reset helpers: class/common and permission helpers (`cil_reset_class()`, `cil_reset_perm()`, `cil_reset_classperms_list()`), alias/bounds helpers (`cil_reset_alias()`, `cil_reset_user()`, `cil_reset_role()`, `cil_reset_type()`), expression-holder resetters for user/role/type attributes and constraints, MLS helpers (`cil_reset_cats()`, `cil_reset_level()`, `cil_reset_levelrange()`), context-bearing object resetters, SID/order resetters, and default/boolean-if cleanup.

## Control Flow

`cil_reset_ast()` calls `cil_tree_walk(current, __cil_reset_node, NULL, NULL, NULL)`. For each AST node, the dispatcher resets only derived fields for that flavor. Nested objects are handled explicitly: class permission lists are traversed item by item, anonymous `level`, `levelrange`, and `context` objects are recursively reset, while named references are set back to `NULL` for later name resolution.

## State and Persistence Behavior

The reset operation mutates the AST in place. It destroys derived `cil_list` containers but normally passes `CIL_FALSE` so referenced datums are not freed. It clears pointers such as `alias->actual`, `user->bounds`, `role->bounds`, `type->bounds`, resolved contexts, resolved MLS ranges, and resolved class permissions. For class/common relations, it subtracts the common permission offset from class permission values and resets `class->num_perms` to local permissions. This makes the next resolver pass behave as if common association had not yet occurred.

## Dependencies and Integration Points

This file depends on `cil_tree_walk()` from `cil_tree.c`, `cil_list_destroy()` and list iteration macros, symbol-table mapping through `cil_symtab_map()`, logging, and the large CIL data model in `cil_internal.h`. Its main integration point is `cil_resolve_ast()`, which calls `cil_reset_ast()` after optional-block removal containing declarations requires resolution to restart.

## Risks and Edge Cases

The code assumes fields follow ownership conventions: named references are not destroyed, anonymous subobjects are recursively reset, and derived lists can be destroyed without freeing their datum payloads. The manual expression-list cleanup for attributes avoids destroying nested expression stacks, but is easy to get wrong if list ownership changes. Class common reset is subtle because permission values are shifted during resolution and must be shifted back exactly once. A missing flavor in `__cil_reset_node()` can leave stale state across re-resolution.

## Test Signals

Useful tests include policies with disabled optionals containing declarations, repeated classcommon resolution after reset, anonymous and named contexts/ranges through filecon, sidcontext, and userrange, attribute set expressions resolved before and after reset, and classpermission/classmapping constructs using nested sets. Memory-checking tests should ensure list containers are freed while datums remain valid for the next pass.
