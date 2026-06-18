# sources/security-integrity/selinux/libsepol/cil/src/cil_copy_ast.h

## Purpose

`cil_copy_ast.h` declares the internal API for copying CIL AST payloads and whole AST subtrees. It is used by code that needs to clone policy fragments while preserving CIL tree, symbol-table, and payload ownership conventions, especially macro argument preservation and block/inheritance expansion.

## Important APIs, Types, and Functions

The main entry point is `cil_copy_ast(struct cil_db *db, struct cil_tree_node *orig, struct cil_tree_node *dest)`. `dest` is the parent node receiving copied children; for macro calls it may be the call node itself, as noted by the companion source comment.

General helpers include `cil_copy_list` for generic CIL lists, `cil_copy_expr` for expression stacks, `cil_copy_classperms`, `cil_copy_classperms_set`, `cil_copy_classperms_list`, `cil_copy_fill_level`, `cil_copy_fill_levelrange`, `cil_copy_fill_context`, and `cil_copy_fill_ipaddr`.

The header declares copy routines for declaration and statement payload families: blocks, classes, permissions, classpermissions, SIDs, users, roles, types, bounds, aliases, transitions, booleans, AV/type rules, MLS sensitivity/category/level structures, contexts, labeling statements, constraints, calls, optionals, IP addresses, and boolean conditionals.

## Control Flow and Integration

The header itself has no control flow, but it defines the function-pointer-compatible copy routine shape used by the implementation: most payload copy functions accept `struct cil_db *db`, source `void *data`, destination `void **copy`, and destination `symtab_t *symtab`. This uniform signature lets the implementation dispatch by `enum cil_flavor` during `cil_tree_walk`.

Consumers include build-AST and later CIL transformation code. The header includes `cil_internal.h`, `cil_tree.h`, and `cil_symtab.h`, so it is coupled to internal payload definitions and namespace types.

## State and Persistence Behavior

Copy routines declared here mutate caller-owned destination AST nodes and symbol tables. They do not persist data to disk. The interface implies a mixed ownership model: callers receive newly allocated payload/list containers where appropriate, but many strings and resolved datum pointers are shallow-copied because CIL strings are interned and datums often represent shared semantic declarations.

## Dependencies

This header depends directly on internal CIL structures, tree nodes, and symbol tables. Its declarations are intended to match `cil_copy_ast.c`, `cil_build_ast.c` destructors, and flavor definitions from `cil_flavor`.

## Risks and Maintenance Notes

The exported surface is broad and includes some names not defined under the same exact names in the companion source snapshot, such as `cil_copy_permset`, `cil_copy_common`, flavor-specific bounds aliases, exact alias helper names, and `cil_copy_exrp`. The source dispatch uses generic/static routines for several of these roles. Direct external references to stale declarations would be caught only at link time.

Because many helpers expose partially deep-copying semantics, callers must understand which fields are newly allocated and which are shared. Misusing these helpers as if they produced a fully independent clone can create dangling references or namespace confusion when copied fragments outlive their original semantic context.

## Test Signals

Compile/link tests should include code paths that reference exported copy helpers to detect declaration drift. Behavioral tests should call `cil_copy_ast` over representative AST fragments and verify copied payload ownership by destroying both original and copy under sanitizers. Tests should cover list/expression copying, classpermissions, anonymous contexts/levels/ranges, IP address values, duplicate destination declarations, and blockinherit/macro-specific copy behavior.
