# sources/security-integrity/selinux/libsepol/cil/src/cil_resolve_ast.c

## Purpose

`cil_resolve_ast.c` is the core CIL name-binding and semantic expansion pass. It turns strings and parse-time lists into pointers to `cil_symtab_datum` objects, expands `in`, `blockinherit`, macro calls, and tunable conditionals, merges global ordering statements, resolves aliases, binds policy rules to classes/types/roles/users/MLS objects, and enforces placement restrictions while walking the AST in a defined pass order.

## Important APIs, Types, and Functions

The central public entry point is `cil_resolve_ast(struct cil_db *db, struct cil_tree_node *current)`. Name lookup is exposed through `cil_resolve_name()` and `cil_resolve_name_keep_aliases()`, with macro-argument lookup in `cil_resolve_name_call_args()`. Rule and object APIs include `cil_resolve_avrule()`, `cil_resolve_deny_rule()`, `cil_resolve_type_rule()`, `cil_resolve_nametypetransition()`, `cil_resolve_rangetransition()`, `cil_resolve_context()`, and the file/network/device context resolvers. Expression binding is handled by `cil_resolve_expr()`, `cil_resolve_boolif()`, and tunable-specific evaluation helpers. Class permission APIs include `cil_resolve_classperms()`, `cil_resolve_classperms_list()`, `cil_resolve_classpermissionset()`, `cil_resolve_classcommon()`, and `cil_resolve_classmapping()`. Ordering APIs include `cil_resolve_sidorder()`, `cil_resolve_classorder()`, `cil_resolve_catorder()`, and `cil_resolve_sensitivityorder()`.

`struct cil_args_resolve` carries pass-local state: current `db`, resolver pass, changed flag, delayed-destroy list, active block/macro/optional/booleanif context, lists of order statements, before/after `in` statements, and abstract blocks.

## Control Flow

Resolution is multi-pass. `cil_resolve_ast()` initializes tracking lists, then iterates from `CIL_PASS_TIF` to `CIL_PASS_NUM`, calling `cil_tree_walk()` with node, first-child, and last-child callbacks. `__cil_resolve_ast_node()` dispatches by pass and node flavor. Early passes evaluate tunableifs, collect and resolve `in` statements, link and copy block inheritance, mark abstract blocks, copy macro bodies, then resolve macro arguments. Alias passes bind aliasactual statements and collapse alias chains. Later passes resolve ordering, MLS catsets and senscat links, then all remaining policy declarations and rules.

After specific passes, `cil_resolve_ast()` performs batch work: resolves collected `in` lists, marks abstract block subtrees, checks inheritance explosion and loops, merges order lists into `db->sidorder`, `db->classorder`, `db->catorder`, and `db->sensitivityorder`, sets category values, and verifies all SID/class/category/sensitivity declarations are ordered. If an optional block fails lookup, the helper records the optional as disabled; when leaving that subtree, it marks the tree changed and schedules children for destruction. If destroyed optionals contained declarations after macro-copying, resolution resets derived declarations with `cil_reset_ast()` and restarts after `CIL_PASS_CALL1`.

Name lookup first searches visible parent scopes through blocks, blockinherit source parents, macros, calls, and macro arguments, then falls back to root symtabs. In non-qualified mode, dotted names are parsed as explicit block paths unless the name starts with a leading dot, which starts at root. `cil_resolve_name()` normally follows type/sensitivity/category aliases to their actual datums after alias passes.

## State and Persistence Behavior

The resolver mutates AST objects by filling resolved pointers and derived datum lists. It appends resolved attribute expressions to the target attribute's `expr_list`, records user default levels and ranges on `struct cil_user`, stores SID contexts on `struct cil_sid`, adds blockinherit users to `block->bi_nodes`, copies AST subtrees for `in`, blockinherit, macro calls, and selected tunableif branches, and updates database-global ordered lists and category counts. Class common resolution shifts permission values and increments class permission counts. Type attributes record usage bits for expansion, constraints, allow rules, and neverallow rules.

The pass keeps temporary lists and destroys them on exit. Optional disabling does not remove the optional node immediately; it destroys its children after the current traversal and may force a reset/re-resolve cycle.

## Dependencies and Integration Points

The resolver is tightly integrated with `cil_tree` traversal/logging, `cil_symtab` lookup and removal/reinsertion, `cil_copy_ast`, `cil_reset_ast`, `cil_build_ast` anonymous object fill helpers, `cil_verify` ordering checks, `cil_list`, `cil_stack`, and `cil_internal` data definitions. It consumes `enum cil_pass` and `enum cil_sym_index` from the broader CIL internals. It is normally followed by pre/post verification and later policydb conversion.

## Risks and Edge Cases

Resolution order is a major risk: changing pass order can break macros, optional handling, inheritance, alias following, and ordered-list validation. Optional-block disablement is deliberately non-fatal for unresolved names but can require reset of already-derived state. Macro argument resolution temporarily removes local datums if an argument accidentally resolves to a declaration copied inside the call. Inheritance checks limit degenerate exponential copying and detect loops. Dotted name resolution has different behavior depending on `db->qualified_names`, leading dots, abstract blocks, and use in `in` statements. Anonymous levels, ranges, catsets, classpermissions, and IP addresses must be resolved inline because they may never appear in a normal symbol table.

## Test Signals

High-value tests include alias chains and alias loops, optionals that fail inside and outside declarations, macro recursion and macro parameter shadowing, `in` before/after ordering, blockinherit loops and explosive nested inheritance, mixed classorder/unordered classorder merges, category value ordering, anonymous and named MLS ranges, booleanif/tunableif branch copying, xperms resolution, and dotted scope lookup with root-qualified and relative names.
