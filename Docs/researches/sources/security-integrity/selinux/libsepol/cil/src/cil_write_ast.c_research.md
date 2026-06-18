# sources/security-integrity/selinux/libsepol/cil/src/cil_write_ast.c

## Purpose
`cil_write_ast.c` serializes CIL parse/build/resolve/post AST trees back to human-readable CIL-like text. It is a diagnostic and introspection layer over the CIL tree and datum structures rather than a policy compiler stage that mutates policy state. Its output is phase-sensitive: parse-phase output preserves parse tree structure and quoting, while later phases emit semantic CIL forms from typed `struct cil_*` payloads.

## Important APIs, Types, And Functions
The public entry points are `cil_write_ast_node(FILE *out, struct cil_tree_node *node)` and `cil_write_ast(FILE *out, enum cil_write_ast_phase phase, struct cil_tree_node *node)`. `cil_write_ast_node` handles a single typed AST node through a large `node->flavor` switch, and `cil_write_ast` drives `cil_tree_walk()` with phase-specific callbacks.

Important local helpers include `datum_or_str()` and `datum_to_str()` for resolved datum names versus saved source strings; `write_expr()` for CIL expression lists; `write_classperms()` and `write_classperms_list()` for class/permission groups and classpermission sets; `write_permx()` for ioctl/nlmsg extended permissions; `write_level()`, `write_range()`, `write_context()`, and `write_ipaddr()` for MLS/security context values; `write_constrain()` for constraint expression bodies; and `write_call_args()` / `write_call_args_tree()` for resolved and parse-tree macro call arguments.

The switch covers policy declaration, conditional, macro, access-vector rule, type/role/user, MLS, labeling, network, hardware, filesystem, and capability node flavors. Examples include `CIL_BLOCK`, `CIL_MACRO`, `CIL_CALL`, `CIL_MLS`, `CIL_DEFAULTUSER`, `CIL_CLASS`, `CIL_CLASSPERMISSIONSET`, `CIL_PERMISSIONX`, `CIL_SIDCONTEXT`, `CIL_BOOL`, `CIL_LEVELRANGE`, `CIL_USERATTRIBUTESET`, `CIL_AVRULE`, `CIL_AVRULEX`, `CIL_TYPE_RULE`, `CIL_NAMETYPETRANSITION`, `CIL_CONSTRAIN`, `CIL_FILECON`, `CIL_PORTCON`, `CIL_NODECON`, `CIL_GENFSCON`, `CIL_FSUSE`, `CIL_POLICYCAP`, and `CIL_IPADDR`.

## Control Flow
For parse phase, `cil_write_ast()` calls `cil_tree_walk()` with parse callbacks. The node callback indents by `depth`, prints `(` or `()` for data-less grouping nodes, quotes parse tokens containing whitespace, and otherwise prints the token as-is. First-child and last-child callbacks adjust indentation and emit closing parentheses.

For build/resolve/post phases, `cil_write_ast()` uses CIL callbacks. The node callback specially handles `CIL_SRC_INFO` by emitting `;;* lms`, `;;* lmx`, and `;;* lme` source mapping markers; other nodes are indented and passed to `cil_write_ast_node()`. The first/last child callbacks increase indentation for nested constructs except root and source-info wrappers, and print closing parens for compound forms. Class/common/map-class nodes set `CIL_TREE_SKIP_HEAD` because their permission children are emitted inline by `write_node_list()`.

`cil_write_ast_node()` mostly prints one balanced CIL form per node, with child-bearing forms leaving the closing parenthesis for the tree-walk last-child callback. Helpers choose between resolved datum pointers and unresolved string fields so the writer can represent partially resolved ASTs as well as post-resolution trees.

## State And Persistence
The file does not own durable state. It reads AST node payloads, list contents, datum names, source-location metadata, and resolved/unresolved string fields, then writes to the caller-provided `FILE *out`. It does not allocate persistent objects or mutate the CIL database. The only state it maintains is traversal indentation in `struct cil_write_ast_args`.

## Dependencies And Integration Points
It depends on CIL internals from `cil_internal.h`, flavor constants from `cil_flavor.h`, list traversal from `cil_list.h`, logging from `cil_log.h`, symbol datum shape from `cil_symtab.h`, tree walking from `cil_tree.h`, and its public declarations in `cil_write_ast.h`. It also relies on policy constants such as `SEPOL_OK`, `SEPOL_ERR`, `SEPOL_ALLOW_UNKNOWN`, `AVRULE_ALLOWED`, and related rule kind values.

Integration is centered on `cil_tree_walk()` and the shape of every `struct cil_*` payload referenced by `node->flavor`. New CIL AST node flavors or new enum values require serializer updates here or they fall into placeholder output such as `<?RULE:...>`, `<?OP>`, `<?DEFAULT>`, `<?PROTOCOL>`, or `<?FILETYPE>`.

## Risks
The main correctness risk is drift between parser/build/resolution structures and the serializer switch. Because the file has many manual format branches, a new node field or enum value can silently produce placeholder text or malformed CIL. Some string fields are printed directly and some are quoted, so caller invariants around stored strings matter for round-trip readability. `write_call_args()` appears to emit an extra trailing space for declared string arguments, which may be harmless but can complicate exact output comparisons. `inet_ntop()` failures degrade to `<?IPADDR>`, which is useful diagnostically but not valid policy syntax.

## Test Signals
This subset does not include direct unit tests for `cil_write_ast.c`. Indirect signals come from the broad CIL build/resolve/copy/integration tests registered in `CilTest.c`, especially tests for macros, constraints, contexts, MLS constructs, labeling rules, IP addresses, and extended permissions. Stronger direct tests would compare parse/build/resolve writer output for representative nodes, unresolved string fallback paths, source-info marker handling, and unsupported enum fallback markers.
