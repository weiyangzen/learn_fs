# sources/security-integrity/selinux/libsepol/cil/src/cil_build_ast.c

## Purpose

`cil_build_ast.c` converts the parser tree for SELinux CIL policy input into the typed CIL AST used by later libsepol phases. It is the first major semantic pass after parsing: it verifies list shapes, allocates the correct `cil_*` structures, attaches them to `cil_tree_node` objects, inserts declarative objects into the appropriate symbol tables, records source locations, and rejects statements that are syntactically valid but illegal in the current AST context.

The file also owns many destroy routines for AST payload structures created here. Those destructors encode the ownership model: most strings are interned or parser-owned pointers and are not freed, while lists, anonymous embedded contexts/levels, ebitmaps, and symtab datums are destroyed by the matching payload destructor.

## Important APIs, Types, and Functions

`struct cil_args_build` is the walker state passed through `cil_tree_walk`. It tracks the current destination AST node plus contextual ancestors that affect legality: active `tunif`, `in`, `macro`, `optional`, and `boolif` nodes.

Declaration helpers include `cil_gen_declared_string`, `cil_allow_multiple_decls`, `cil_add_decl_to_symtab`, `cil_gen_node`, and `cil_clear_node`. `cil_gen_node` is the central declaration path: it verifies the name, finds the parent namespace symbol table, sets node data/flavor, inserts the datum, and checks macro parameter shadowing. `cil_add_decl_to_symtab` handles duplicate declaration policy, allowing configured multiple declarations for selected flavors and special repeated declarations for optionals and policycaps.

Syntax and list helpers include `cil_fill_list`, `cil_fill_perms`, `cil_fill_classperms`, `cil_fill_classperms_list`, `cil_gen_expr`, `cil_gen_constraint_expr`, `cil_fill_context`, `cil_fill_levelrange`, `cil_fill_level`, `cil_fill_cats`, `cil_fill_integer`, `cil_fill_integer64`, and `cil_fill_ipaddr`. These helpers translate parse-tree list/string forms into CIL list structures and embedded payload objects.

Generator functions cover nearly the full CIL statement surface: blocks, inheritance, macros and calls, classes, commons, permissions, classpermissions, users, roles, types, aliases, attributes, booleans, tunables, conditionals, AV rules, extended permissions, type and range transitions, MLS sensitivities/categories/levels, constraints, contexts, labeling statements, defaults, policycaps, `handleunknown`, `mls`, and source-info records. `parse_statement` is the large keyword dispatcher that maps `CIL_KEY_*` interned strings to those generator functions.

Destroy functions mirror the generator families. Important patterns include `cil_destroy_classperms_list` deep-destroying mixed classperm/classperm-set items, `cil_destroy_*attributeset` destroying string and datum expression lists with different ownership flags, `cil_destroy_context` destroying anonymous level ranges only when `range_str` is absent, and `cil_destroy_block` unlinking blockinherit back-references from `bi_nodes`.

## Control Flow

`cil_build_ast` initializes `cil_args_build` and walks the parse tree with `cil_tree_walk`. `__cil_build_ast_node_helper` processes only list heads, rejects empty non-root lists, runs `check_for_illegal_statement`, calls `parse_statement`, then advances the current AST pointer to the newly created node. For leaf-like statements it sets `CIL_TREE_SKIP_NEXT` so the walker does not descend into data lists that are not policy statement bodies.

`__cil_build_ast_first_child_helper` records context when the current AST node is a tunableif, in-statement, macro, optional, or booleanif. `__cil_build_ast_last_child_helper` pops the AST pointer back to the parent, clears contextual state, restores outer optional state for nested optionals, and destroys converted parse-tree children to reduce peak memory use.

Most `cil_gen_*` functions follow the same pattern: check arguments, verify exact parse syntax through `__cil_verify_syntax`, allocate/init the payload, read interned strings or child lists from the parse tree, perform statement-specific keyword/value checks, assign `ast_node->data` and `ast_node->flavor`, and return `SEPOL_OK`. On failure they log a statement-specific message, destroy partially initialized payloads, and clear declarative AST nodes when needed.

Expression parsing is recursive. Generic set and conditional expressions map interned operator strings to `CIL_AND`, `CIL_OR`, `CIL_NOT`, `CIL_EQ`, `CIL_NEQ`, `CIL_XOR`, `CIL_ALL`, and `CIL_RANGE`, verify the operator grammar for the target flavor, and build nested `cil_list` stacks. Constraint expressions use a separate operator and operand grammar because left/right operands may be constraint slots such as `u1`, `r2`, `t3`, or MLS low/high fields.

## State and Persistence Behavior

The AST build is in-memory only. Persistent effects are mutations to the caller-owned `cil_db`, AST tree, symbol tables, and helper lists. New declarations are inserted into namespace symbol tables found by `cil_get_symtab`; root-level declared strings are added to the root string symtab and `db->declared_strings`. Repeated declarations can cause a node to reuse an existing datum rather than keep the newly allocated payload.

Some generators deliberately mutate the parse tree while building the AST. `cil_gen_boolif` and `cil_gen_tunif` remove the parsed expression subtree after translating it to `str_expr`. `cil_gen_macro` removes the macro parameter list so the walker processes only macro body statements. The last-child walker destroys parse-tree children once converted.

Strings are compared by pointer against `CIL_KEY_*` constants, so this file assumes parser/strpool interning. Numeric and IP address fields are materialized into integer or `inet_pton` binary forms when the grammar permits literal values, while unresolved identifiers remain as `*_str` pointers for later resolution.

## Dependencies and Integration Points

This file integrates with `cil_parser` parse-tree nodes, `cil_verify` syntax/name/expression validators, `cil_symtab` namespace storage, `cil_tree` traversal and destruction, `cil_list`, `cil_mem` allocators, `cil_log`, `cil_strpool`, and libsepol policy constants such as `POLICYDB_VERSION_COND_XPERMS` and unknown-class handling values. It calls `cil_copy_ast` when preserving macro call argument trees.

Later CIL phases depend on its exact flavor assignment, symbol-table insertion, `*_str` fields, anonymous embedded objects, and expression stack shape. The copy/resolve/compiler phases also rely on destructor ownership conventions established here.

## Risks and Edge Cases

The large `parse_statement` dispatch table is a maintenance hotspot: adding a CIL keyword requires coordinated syntax verification, generator/destroy/copy support, legality checks, and later resolver support. Missing one of those can produce parse acceptance followed by later resolution or copy failures.

Duplicate declaration handling is subtle. Some duplicate declarations intentionally reuse existing datums, while others are fatal. The code must destroy abandoned newly allocated payloads on `SEPOL_EEXIST` paths to avoid leaks and must avoid clearing AST nodes that were rebound to existing datums.

The build pass relies heavily on interned pointer equality for keyword checks. Any caller that bypasses the normal parser/string pool would break keyword matching. Context restrictions are also centralized in `check_for_illegal_statement`; new container flavors or conditional-rule allowances must be added there.

Error cleanup has many partial-object paths. Embedded anonymous objects such as contexts, level ranges, category expressions, and permissionx objects are owned only under certain `*_str == NULL` conditions, so regressions can double-free or leak. Range parsers validate shape and integer conversion but generally do not enforce ordering such as low <= high in this file; later validation must cover semantic consistency.

## Test Signals

Good test coverage should compile valid CIL containing every major statement family and assert successful AST build plus later resolution. Negative tests should cover duplicate declarations, illegal statements inside macro/optional/in/booleanif/tunableif contexts, invalid boolean/default/handleunknown/file type keywords, malformed class-permission and constraint expressions, excessive class permission counts, invalid numeric ranges, invalid IP literals, macro parameter shadowing and duplicate parameters, and `preserve_tunables` behavior.

Memory tests should run malformed-policy corpora under ASan/Valgrind because most risk is partial-construction cleanup. Regression tests should specifically exercise block inheritance, macro calls with copied argument trees, named versus anonymous contexts/levels/ranges, declared-string parameters, and policy-version gating for conditional extended permissions.
