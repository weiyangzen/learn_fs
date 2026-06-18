# sources/security-integrity/selinux/libsepol/cil/src/cil_copy_ast.c

## Purpose

`cil_copy_ast.c` deep-copies CIL AST subtrees into another AST location while preserving the semantic ownership rules needed by block inheritance, macro calls, in-statements, and cloned policy fragments. It creates new tree nodes and new payload structs, rebuilds symbol-table entries for declarative nodes, shallow-copies interned strings and already-resolved datum references where appropriate, and deep-copies mutable nested structures such as expression lists, anonymous contexts, levels, level ranges, IP addresses, and classpermission lists.

## Important APIs, Types, and Functions

`struct cil_args_copy` carries the original destination (`orig_dest`), current destination parent (`dest`), and `cil_db` through the tree walker. `cil_copy_ast` is the public entry point and treats `dest` as the parent node into which copied children are appended.

Generic copying helpers include `cil_copy_list`, `cil_copy_expr`, `cil_copy_classperms`, `cil_copy_classperms_set`, `cil_copy_classperms_list`, `cil_copy_fill_level`, `cil_copy_fill_levelrange`, `cil_copy_fill_context`, and `cil_copy_fill_ipaddr`. These preserve interned string/datum pointer identity while allocating new list and embedded object containers.

There are copy routines for most AST payload families: ordered lists, blocks, blockabstract/blockinherit, policycaps, permissions, class mappings and classpermissions, SID/user/role/type declarations and set statements, aliases, transitions, bool/tunable conditionals, AV and extended-permission rules, deny/type rules, MLS constructs, contexts and labeling statements, constraints, macros/calls, optionals, defaults, bounds, `handleunknown`, `mls`, and source-info records.

`__cil_copy_node_helper` is the dispatch and insertion engine. It maps `orig->flavor` to the correct copy function, locates a destination symbol table for declarative flavors, invokes the copy routine, creates the destination tree node, updates declaration symbol tables with `cil_add_decl_to_symtab`, enforces flavor compatibility, updates blockinherit back-references, appends the new node to the parent, and descends into children when present.

## Control Flow

`cil_copy_ast` initializes walker state and calls `cil_tree_walk(orig, __cil_copy_node_helper, NULL, __cil_copy_last_child_helper, &extra_args)`. The node helper handles a pre-order copy: select copy routine by flavor, copy payload data, allocate a new `cil_tree_node`, attach it to the destination parent, and if the source has children, set `args->dest` to the new node so child copies nest below it. The last-child helper pops `args->dest` back to the parent after a child subtree is complete.

Declarative nodes take an additional path. For flavors at or above `CIL_MIN_DECLARATIVE`, the helper converts flavor to symbol-table index, finds the destination namespace symbol table, and inserts the copied datum using the original datum name. Duplicate block and macro behavior is special for block inheritance: duplicate blocks can append another node to an existing datum, and duplicate macros may be skipped only while inheriting a block. Other incompatible or duplicate named objects generally produce errors.

Some payload copy routines allocate only a fresh initialized declaration object and let `__cil_copy_node_helper` set datum metadata through symbol-table insertion. Nondeclarative payloads copy statement fields directly. `cil_copy_call` recursively copies a call's `args_tree`, preserving macro pointer and copied flag. `cil_copy_avrule` branches between normal classperms lists and inline/named extended permissionx payloads.

## State and Persistence Behavior

The copy is in-memory and mutates the destination AST and its symbol tables. It does not clone all semantic state: many resolved pointers are shallow-copied, including interned strings, existing datums in expression lists, alias actual pointers, block references, class/common references, macro references, and declared-string references. This is intentional for data that is global, interned, or re-resolved later, but it means the copy is not an independent serialization boundary.

Expression and classpermission lists are structurally copied, so the copied tree can own its list containers independently. Anonymous embedded contexts, levels, ranges, category sets, and IP address values are copied into new allocations. Named references remain as strings or datums and are expected to resolve in the destination namespace.

For blockinherit nodes, if the referenced block is already resolved, the copied node is appended to `block->bi_nodes`; otherwise the resolver will handle it later. This allows copying before blockinherit resolution, especially for in-statement handling.

## Dependencies and Integration Points

The file depends on `cil_internal`, `cil_log`, `cil_mem`, `cil_tree`, `cil_list`, `cil_symtab`, `cil_copy_ast.h`, `cil_build_ast.h`, `cil_strpool`, and `cil_verify`. Its most important integration point is `cil_add_decl_to_symtab` from the build-AST layer, which keeps copied declarations consistent with normal declarations. It also relies on flavor-to-symtab mapping, tree walking, node-to-string logging, and datum macros such as `DATUM`, `FLAVOR`, and `NODE`.

`cil_build_ast.c` calls `cil_copy_ast` when preserving macro call argument trees. Resolver and inheritance code depend on this file to clone AST fragments without corrupting namespaces or losing source location metadata.

## Risks and Edge Cases

The dispatch switch must stay synchronized with all AST flavors. Adding a new flavor without a copy case causes subtree copy failures for policies that use the new construct in macros, block inheritance, or other clone paths.

Shallow versus deep copy boundaries are subtle. Resolved pointers copied from the source may be correct for shared global datums but dangerous if a future field points into a namespace-specific or lifetime-limited object. Conversely, deep-copying datum references incorrectly would break identity expectations used by later phases.

Duplicate handling differs by construct. Blocks and macros have special inheritance behavior, while named classpermissions, permissionx, catsets, levels, levelranges, contexts, and IP addresses reject redefinition. This can surface only in clone paths, so normal parser tests may miss it.

There are implementation details worth watching: `cil_copy_condblock` initializes through a local `new = *copy` even though callers pass an uninitialized `data` pointer variable; it then overwrites `*copy` after init, so behavior depends on the init routine not reading the incoming pointer value. Header/source drift also exists for several exact copy-helper names exposed in the header but implemented through generic or static helpers in this file.

## Test Signals

Tests should copy AST fragments containing every supported flavor through macro call arguments, block inheritance, and nested blocks. Assertions should verify destination tree shape, source line/hll offset preservation, symbol-table insertion, duplicate declaration behavior, and that inherited duplicate blocks/macros behave differently from ordinary redefinitions.

Memory and lifetime tests should stress copying of anonymous contexts, levels, ranges, category sets, expression lists, permissionx expressions, call argument trees, and blockinherit back-reference lists under ASan/Valgrind. Negative tests should include incompatible duplicate declarations in a destination namespace, duplicate named anonymous-capable objects, unknown flavor handling, and copy failures inside recursive call-argument trees.
