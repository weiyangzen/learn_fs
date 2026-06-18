# sources/security-integrity/selinux/libsepol/cil/src/cil_build_ast.h

## Purpose

`cil_build_ast.h` declares the public build-AST interface for CIL parser-tree conversion and exposes many statement-specific generator, filler, and destructor helpers used by neighboring CIL implementation files. It is broader than a minimal interface: besides `cil_build_ast`, it exports construction/destruction routines for most AST payload types, symbol-table declaration helpers, expression/list fillers, integer/IP parsing helpers, and context/MLS helpers.

## Important APIs, Types, and Functions

The main entry point is `cil_build_ast(struct cil_db *db, struct cil_tree_node *parse_tree, struct cil_tree_node *ast)`, which turns a parse tree into a typed AST rooted at `ast`.

Core declaration APIs are `cil_add_decl_to_symtab`, `cil_gen_declared_string`, and `cil_gen_node`. These are important integration points for code that constructs AST nodes outside the main parser walk because they preserve name validation, namespace lookup, duplicate declaration policy, and macro-parameter shadowing checks.

The header groups most CIL statement families as generator/destroy pairs: blocks and inheritance, classes/common/permissions/classpermission sets, SIDs, users, roles, types and aliases, booleans/tunables/conditionals, AV/type rules, MLS sensitivity/category/level constructs, constraints, contexts, labeling statements, macros/calls, optionals, policycaps, IP addresses, bounds, defaults, `handleunknown`, `mls`, and source-info records.

Helper exports include `cil_gen_expr`, `cil_gen_constrain_expr`, `cil_fill_classperms_list`, `cil_destroy_classperms_list`, `cil_fill_levelrange`, `cil_fill_context`, `cil_fill_cats`, `cil_fill_integer`, `cil_fill_integer64`, `cil_fill_ipaddr`, and `cil_fill_level`.

## Control Flow and Integration

This header does not implement control flow, but its declarations define the build contract used by `cil_build_ast.c` and by other CIL phases that need to create or destroy compatible AST payloads. The caller provides a `cil_db` for policy options and symbol tables, parse/AST tree nodes from `cil_tree`, and flavor/symbol-table constants from `cil_flavor` and `cil_symtab`.

Many functions accept `struct cil_tree_node *parse_current` plus `struct cil_tree_node *ast_node`; generators generally read parse-node siblings, fill `ast_node->data`, and set `ast_node->flavor`. Destroy functions accept payload pointers, not tree nodes, reflecting that tree destruction dispatches separately by flavor.

## State and Persistence Behavior

The header exposes routines that mutate caller-owned AST nodes, symbol tables, and `cil_db` auxiliary lists. It does not define any persistent on-disk behavior. The declared APIs assume the same ownership model as the implementation: interned strings and resolved datum references are usually shallow-owned, while expression lists, anonymous nested contexts/levels/ranges, ebitmaps, and symtab datums are owned by the payload destructor that matches the payload flavor.

## Dependencies

The header includes `stdint.h`, `cil_internal.h`, `cil_flavor.h`, `cil_symtab.h`, `cil_tree.h`, and `cil_list.h`. Those dependencies expose internal CIL payload structs and make this a private/internal libsepol header rather than a narrow external API.

## Risks and Maintenance Notes

Because this header exports a very large surface, drift between declarations and implementation is a risk. In this snapshot, some compatibility-style declarations, such as flavor-specific bounds generator names and some list/constrain helpers, are not defined under those exact names in the companion `cil_build_ast.c`; the implementation instead uses generic helpers such as `cil_gen_bounds` in the dispatcher. Consumers should verify exact symbol availability before depending on those names.

The many exported destroy functions make ownership discipline visible but also fragile: a caller can easily use a destructor for a partially initialized object or an object whose nested `*_str` fields determine ownership. Any new AST payload field must be reflected in both the implementation destructor and, if external construction is needed, the header contract.

## Test Signals

Build tests should catch header/source drift by compiling every CIL source file that includes this header with warnings enabled. API-level tests should exercise construction/destruction of payloads through declared helpers, especially anonymous contexts/levels/ranges, expression lists, classpermissions, and duplicate symbol-table declarations. Link tests are useful because stale declarations can compile but fail when an external user references a function not implemented under the advertised name.
