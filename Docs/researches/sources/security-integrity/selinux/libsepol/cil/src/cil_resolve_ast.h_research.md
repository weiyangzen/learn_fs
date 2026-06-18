# sources/security-integrity/selinux/libsepol/cil/src/cil_resolve_ast.h

## Purpose

`cil_resolve_ast.h` publishes the CIL resolver interface. It exposes both the full AST resolution pass and many flavor-specific helper functions used by other compilation phases or tests.

## Important APIs, Types, and Functions

The primary API is `cil_resolve_ast(struct cil_db *db, struct cil_tree_node *current)`. The header also declares resolver functions for class permissions, rules, aliases, bounds, users, roles, MLS categories/levels/ranges, constraints, contexts, context-bearing statements, ordering statements, block inheritance, `in`, macro calls, expressions, booleanifs, tunableifs, and scoped name lookup. It includes `cil_internal.h` and `cil_tree.h`, so consumers see the CIL database and tree-node types.

## Control Flow and Integration

Most declarations correspond to implementation dispatch cases in the multi-pass resolver. External code can call specific resolvers when constructing or testing individual AST fragments, but normal policy compilation should call `cil_resolve_ast()` so pass ordering, delayed `in` resolution, optional handling, and ordered-list merging are all honored.

## State and Persistence Behavior

The declared functions generally mutate AST nodes and database fields in place, converting string fields to resolved datum pointers or derived lists. Name lookup APIs return borrowed datum pointers owned by the relevant symtab/datums, not newly allocated copies.

## Dependencies and Risks

The broad exported surface creates coupling to CIL internals and makes signature changes expensive. Calling helpers outside the full pass can bypass prerequisites such as alias processing, classcommon resolution, or MLS ordering. Callers must obey resolver state assumptions: valid `db`, built AST symtabs, and correct parse/build-time fields.

## Test Signals

Compile API tests should cover headers for downstream users. Behavioral tests should use both `cil_resolve_ast()` end-to-end and targeted helper tests for name lookup, expression resolution, class permissions, and context resolution.
