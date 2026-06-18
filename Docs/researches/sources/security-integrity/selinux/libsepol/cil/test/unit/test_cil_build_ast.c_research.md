# Research: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_build_ast.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-008357`: lines 1-10057, `Docs/researches/chunks/subset-b-008357_research.md`
- `subset-b-008358`: lines 10058-20682, `Docs/researches/chunks/subset-b-008358_research.md`
- `subset-b-008359`: lines 20683-22965, `Docs/researches/chunks/subset-b-008359_research.md`

## Chunk Research

### subset-b-008357: lines 1-10057

# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_build_ast.c lines 1-10057

## Chunk Scope

This research covers the first chunk of `test_cil_build_ast.c`, from the license/header through line 10057. The chunk begins a very large CuTest unit-test file for libsepol's CIL AST builder and ends in the middle of `test_cil_gen_avrule_targetemptyparen_neg`; later AV-rule cases and AST-dispatch helper tests are outside this chunk.

## Purpose

This chunk validates the low-level CIL parse-tree-to-AST builder functions in `../../src/cil_build_ast.h`. The tests build synthetic CIL parse trees from token arrays with `gen_test_tree`, call individual `cil_gen_*`, `cil_fill_*`, `cil_parse_to_list`, `cil_set_to_list`, and `cil_gen_expr_stack` routines directly, and assert their return codes and selected AST fields.

The primary behavioral target is parser robustness: each grammar production has a success case and many malformed-input cases covering null pointers, missing required tokens, extra tokens, unexpected nested lists, empty lists, duplicate symbols, invalid operators, and wrong expression domains.

## File Setup and Local Helpers

The chunk includes:

- `<sepol/policydb/policydb.h>` for SELinux/libsepol status and policy constants.
- `CuTest.h` and `CilTest.h` for the test framework and helper fixtures.
- `test_cil_build_ast.h` for suite declarations used by the full file.
- Private implementation headers `../../src/cil_build_ast.h` and `../../src/cil_tree.h`, making this a white-box unit test.

The file forward-declares private helpers:

- `__cil_build_ast_node_helper(struct cil_tree_node *, uint32_t *, void *)`
- `__cil_build_ast_last_child_helper(struct cil_tree_node *, void *)`

Only declarations appear in this chunk; the direct tests for these helpers occur after the current line range.

The local `struct cil_args_build` mirrors the argument bundle passed to AST traversal helpers: `ast`, `db`, `macro`, and `tifstack`. `gen_build_args()` heap-allocates this structure with `cil_malloc` and stores those pointers without ownership transfer or cleanup in this chunk.

## Important APIs and Behaviors Covered

### Generic tree/list conversion

The first tests cover `cil_parse_to_list` and `cil_set_to_list`.

- `cil_parse_to_list` is checked with an `allow` rule permission list and `CIL_AST_STR` list item flavor.
- Negative cases assert `SEPOL_ERR` for null parse node and null output list.
- `cil_set_to_list` converts CIL set syntax into `struct cil_list`, including nested sublists.
- Negative cases check null tree node, null `cl_head`, and null output list.

These tests exercise the builder's base assumption that parse tree nodes are linked through `cl_head`, `next`, and child-list nodes.

### Namespace and block forms

The chunk covers:

- `cil_gen_block`
- `cil_destroy_block`
- `cil_gen_blockinherit`
- `cil_gen_in`

`cil_gen_block` creates a `CIL_BLOCK` node, sets `data`, and preserves the `is_abstract` argument. Its failure cases cover missing block name, list-valued name, null database, null current parse node, null AST node, and null AST parent. `cil_destroy_block` is expected to clear the AST node data via the destroy path.

`cil_gen_blockinherit` accepts exactly a scalar inherited block name. Tests reject list names, missing names, extra tokens, null database, null current node, and null AST node.

`cil_gen_in` handles an `in` statement with a block name and nested body. Tests reject missing block name, extra body elements after the nested statement list, null database/current/AST node, and malformed parse nodes.

### Classes, permissions, permission sets, and class maps

The chunk heavily exercises class/permission generation:

- `cil_gen_perm`
- `cil_gen_permset`
- `cil_gen_perm_nodes`
- `cil_fill_permset`
- `cil_gen_class`
- `cil_fill_classpermset`
- `cil_gen_classpermset`
- `cil_gen_classmap_perm`
- `cil_gen_classmap`
- `cil_gen_classmapping`
- `cil_gen_common`

The normal `cil_gen_class` path builds a `CIL_CLASS`, attaches child permission nodes, and validates that `cl_tail` and `data` are set. It also permits a class with no permissions. Negative cases check malformed names, missing `class`, permissions outside a list, multiple permission lists, nested permission lists, and null arguments.

`cil_gen_perm_nodes` inserts generated permissions into a class permission symtab. One important negative case destroys `test_cls->perms` before insertion and expects `SEPOL_ENOMEM`, so this chunk explicitly tests allocation/symtab failure propagation.

`cil_fill_classpermset` and `cil_gen_classpermset` accept both anonymous permission lists like `(char (write))` and named permission-set references like `(char perms)`. They reject empty permission lists, missing class names, nested unexpected lists, extra tokens, and null output structures.

`cil_gen_classmap_perm` tests classmap permission insertion and duplicate detection. The duplicate case calls `cil_gen_classmap` first, then tries to generate the same classmap permission and expects `SEPOL_EEXIST`.

`cil_gen_classmapping` handles both anonymous class/permission-set tuples and named permission-set references. It rejects missing classmap name, missing classmap permission, missing mapped permission sets, empty anonymous permission sets, and null database/current/AST node.

`cil_gen_common` validates common permission blocks and rejects missing names, duplicate permission lists, nested permissions, and empty permission lists.

### SID, type, role, bounds, and alias declarations

This chunk covers declaration generators for:

- `cil_gen_sid`
- `cil_gen_sidcontext`
- `cil_gen_type`
- `cil_gen_typeattribute`
- `cil_gen_typebounds`
- `cil_gen_typepermissive`
- `cil_gen_typealias`
- `cil_gen_typeattributeset`
- `cil_gen_userbounds`
- `cil_gen_role`
- `cil_gen_roletransition`
- `cil_gen_roleallow`
- `cil_gen_rolebounds`

The declaration pattern is consistent: create a small tokenized CIL statement, initialize a DB and AST node, set `test_ast_node->parent = test_db->ast->root` where required, call the generator, and assert `SEPOL_OK` plus expected AST flavor/data for success cases.

`cil_gen_sidcontext` is notable because it accepts both anonymous context syntax and named context references. Negative cases cover half-formed contexts, missing SID name, empty statement, missing context, duplicate context names, null database/current/AST node.

`cil_gen_typeattributeset` accepts scalar type names and expression forms such as `(and test_t test2_t)` and `(not notypes_t)`. It also treats `(not attr)` as a valid exclusion expression. It rejects empty `(not)`, missing attribute name, name in parentheses, empty lists, list-valued members where scalar values are expected, extra tokens, and null inputs.

`cil_gen_roletransition` is a two-argument API in this file, unlike many other generators: `cil_gen_roletransition(parse_current, ast_node)`. Its tests mutate linked-list pointers to simulate missing source, target, and result fields. It does not take `struct cil_db *` in this chunk.

`cil_gen_roleallow` and `cil_gen_rolebounds` validate role relationship statements and include field assertions for `src_str` and `tgt_str`.

### Boolean, tunable, and conditional AST forms

The chunk tests expression parsing and conditional blocks:

- `cil_gen_expr_stack` with `CIL_BOOL`
- `cil_gen_boolif`
- `cil_gen_tunif`
- `cil_gen_condblock`
- `cil_gen_bool` for both `CIL_BOOL` and `CIL_TUNABLE`

Boolean expression tests cover `and`, `or`, `xor`, `not`, `eq`, `neq`, nested expressions, missing operators, empty argument lists, missing operands, extra operands, null current node, and null output stack.

`cil_gen_boolif` and `cil_gen_tunif` validate `true` and `false` branch blocks, multiple branch blocks, nested boolean/tunable expressions, scalar condition references, missing true-list blocks, empty conditions, unknown condition keywords, extra parentheses, bad operators, and null arguments.

`cil_gen_condblock` validates both `CIL_CONDTRUE` and `CIL_CONDFALSE` blocks and rejects missing nested rule lists and extra tokens.

`cil_gen_bool` creates both boolean and tunable AST nodes, checks parsed `true`/`false` values, and rejects missing value, invalid boolean strings, missing names, extra names, and null inputs.

### Range transitions and name transitions

The chunk covers:

- `cil_gen_nametypetransition`
- `cil_gen_rangetransition`

`cil_gen_nametypetransition` expects a string/name, source type, target type, class, and destination type. It has precise negative tests for each missing field and for each field incorrectly represented as a parenthesized sublist.

`cil_gen_rangetransition` accepts named level ranges and anonymous level forms, including anonymous low or high level values. It rejects null database/current/AST node, missing source/target/class/low/high fields, parenthesized scalar fields, invalid anonymous level syntax, and extra tokens.

### Constraint and MLS constraint expressions

The densest section in this chunk targets `cil_gen_expr_stack` with `CIL_MLSCONSTRAIN` and `CIL_CONSTRAIN`. It constructs `struct cil_constrain`, initializes `classpermset`, fills it from the parse tree with `cil_fill_classpermset`, and parses the expression into `cons->expr`.

Operators and domains covered include:

- Equality and inequality: `eq`, `neq`
- Unary negation: `not`
- Binary logical operators: `or`, `and`
- MLS dominance operators: `dom`, `domby`, `incomp`
- Entity keywords: `t1`, `t2`, `r1`, `r2`, `u1`, `u2`
- MLS keywords: `l1`, `l2`, `h1`, `h2`
- Symbol references such as `type_t`, `role_r`, and `user`

The tests enforce domain restrictions. For example, comparing `t1` to `type_t`, `r1` to `role_r`, or `u1` to `user` is accepted, while self comparisons such as `t1` to `t1`, `r1` to `r1`, `u1` to `u1`, or invalid MLS level usage in ordinary `CIL_CONSTRAIN` are rejected. The chunk also checks left-keyword restrictions such as `eq h2 h1`, missing operands, operands in parentheses, extra operands, operators in parentheses, null output stack, null/empty current expression, and calling into a nested expression at the wrong parse node.

### AV rule start

The chunk begins AV-rule testing:

- `cil_gen_avrule` with `CIL_AVRULE_ALLOWED`

Successful cases include anonymous class/permission lists and named permission-set references. The main success case asserts source string, target string, class string, AST flavor `CIL_AVRULE`, and the populated permission list with `CIL_AST_STR` items matching parse-tree permission tokens.

Negative cases in this chunk include extra trailing token after the classperm set, source represented as a list, empty source list, target represented as a list, and the beginning of an empty target-list test. The empty target-list test body is incomplete at line 10057 and continues into the next chunk.

## Control Flow Pattern

Nearly every test follows the same sequence:

1. Declare a null-terminated `char *line[]` token stream representing a CIL form.
2. Call `gen_test_tree(&test_tree, line)` to synthesize a `struct cil_tree`.
3. Allocate a `struct cil_tree_node *test_ast_node` with `cil_tree_node_init`.
4. Allocate a `struct cil_db *test_db` with `cil_db_init` where the target API requires a database.
5. Set AST parent and line metadata when the generator expects a valid insertion context.
6. Navigate the parse tree via `root->cl_head->cl_head`, `next`, and `cl_head` chains.
7. Call the target generator/filler/parser.
8. Assert `SEPOL_OK`, `SEPOL_ERR`, `SEPOL_ENOMEM`, or `SEPOL_EEXIST`; selected success tests also assert AST data fields, flavors, or list contents.

Negative tests often mutate the generated parse tree after construction, e.g. setting `cl_head` or `next` links to `NULL`, to exercise error paths that are hard to express through a simple token array.

## State and Persistence Behavior

There is no durable persistence, file I/O, or external state in this chunk. All state is in-memory test fixture state:

- `struct cil_db` instances own an AST root and symtabs used by generators.
- `struct cil_tree` instances provide parsed CIL input fixtures.
- `struct cil_tree_node` instances are manually initialized and used as destinations for AST builder output.
- `struct cil_list`, `struct cil_permset`, `struct cil_classpermset`, and `struct cil_constrain` objects are allocated directly for helper-level tests.
- Some objects are explicitly destroyed only where the test target is a destroy function or where failure injection requires it, such as destroying `test_cls->perms` before testing `cil_gen_perm_nodes` error propagation.

The tests intentionally do not exercise final compiled policy output. They validate intermediate AST construction, parse validation, and data attachment only.

## Dependencies and Integration Points

This unit-test chunk integrates tightly with libsepol CIL internals:

- `cil_malloc`, `cil_strdup`, `cil_db_init`, `cil_tree_node_init`, and specific `cil_*_init` routines allocate and initialize fixture state.
- `gen_test_tree` from `CilTest.h` is the parse-tree fixture factory.
- `cil_symtab_insert` is used to seed the class symbol table for permission-node generation.
- Return codes are libsepol constants: `SEPOL_OK`, `SEPOL_ERR`, `SEPOL_ENOMEM`, and `SEPOL_EEXIST`.
- AST flavors such as `CIL_BLOCK`, `CIL_CLASS`, `CIL_COMMON`, `CIL_SIDCONTEXT`, `CIL_TYPE`, `CIL_TYPEATTRIBUTE`, `CIL_TYPEALIAS`, `CIL_ROLE`, `CIL_ROLETRANSITION`, `CIL_BOOL`, `CIL_TUNABLE`, `CIL_ROLEALLOW`, and `CIL_AVRULE` are central assertions.

Because the test includes private headers and forward-declares private helpers, it is coupled to libsepol's internal AST builder contracts rather than only public CIL APIs.

## Risks and Maintenance Notes

- The tests are brittle by design: many assertions depend on exact parse-tree layout through chained `next`/`cl_head` accesses. Changes in `gen_test_tree` or parse-tree shape can break many tests even if high-level CIL semantics remain correct.
- Several success tests only assert `SEPOL_OK` and do not inspect all generated fields. This gives broad grammar coverage but may miss subtle field-assignment regressions.
- Memory management is fixture-oriented. Many initialized trees, databases, lists, and AST nodes are not destroyed in each test, so leak detectors may require test harness-specific suppression or cleanup outside this chunk.
- Some negative cases inject malformed state by mutating linked-list pointers directly. This is useful for defensive-code coverage, but it can produce states a real parser may never create.
- Domain checks in constraint expressions are security-relevant. Regressions here could allow invalid SELinux constraint expressions into later policy compilation phases.
- The chunk boundary cuts through `test_cil_gen_avrule_targetemptyparen_neg`; any merged research must combine this report with the following chunk to avoid treating the AV-rule target-empty case as fully covered here.

## Test Signals

Strong test signals in this chunk:

- Repeated positive/negative pairs for each generator make expected grammar shape explicit.
- Null input tests cover defensive API contracts.
- Extra-token and list-vs-scalar tests cover parser strictness.
- Duplicate permission insertion asserts `SEPOL_EEXIST`.
- Artificial symtab destruction asserts `SEPOL_ENOMEM` propagation.
- Constraint-expression tests cover many valid and invalid SELinux/MLS operator-domain combinations.
- Selected data assertions confirm AST flavor, allocated data presence, boolean values, strings copied from parse nodes, and permission-list item flavors.

Weak or absent signals:

- No end-to-end `cil_build_ast` traversal is covered in this chunk; those tests appear later in the file.
- No compiled binary policy comparison is performed.
- Most tests do not verify cleanup side effects.
- Many generated AST structs are checked only for non-null data and flavor, not full field-by-field equivalence.

### subset-b-008358: lines 10058-20682

# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_build_ast.c lines 10058-20682

## Scope And Purpose

This chunk is the middle and largest section of `test_cil_build_ast.c`, a CUnit test file for libsepol's CIL AST builder. It exercises the parser-to-AST generator helpers in `cil_build_ast.c` by building synthetic CIL token trees with `gen_test_tree`, attaching fresh AST nodes to a `cil_db`, invoking a specific `cil_gen_*`, `cil_fill_*`, `cil_build_ast`, or `__cil_build_ast_node_helper` entry point, and checking `SEPOL_OK`/`SEPOL_ERR`, AST flavor, and selected generated fields.

The range begins inside `test_cil_gen_avrule_targetemptyparen_neg`, so its first covered lines are the setup and assertion for an `allow` rule with an empty parenthesized target. It ends in the setup of `test_cil_build_ast_node_helper_typealias_notype_neg`, before that test's helper call and assertions. The following chunk must be consulted for the remainder of that test and later dispatcher cases.

The primary purpose is executable grammar and validation coverage for CIL AST construction. It checks that valid CIL forms produce the expected AST node kind and internal strings/lists, and that malformed trees, null inputs, missing operands, list-vs-symbol mismatches, bad protocol/address/numeric values, and extra operands are rejected.

## Important APIs, Types, And Functions

Core test harness and setup helpers:

- `CuTest`, `CuAssertIntEquals`, `CuAssertStrEquals`, `CuAssertPtrNotNull`, `CuAssertPtrEquals`, and related assertions provide the CUnit-style test contract.
- `gen_test_tree(&test_tree, line)` converts a NULL-terminated token vector into a `struct cil_tree` parse tree. Most tests then pass `test_tree->root->cl_head->cl_head` as the current list head.
- `cil_db_init(&test_db)` creates a `struct cil_db` with an AST root used as the parent for generated nodes and as the root symbol-table context for named declarations.
- `cil_tree_node_init(&test_ast_node)` allocates the AST node passed to a generator. Tests usually set `test_ast_node->parent = test_db->ast->root` and `test_ast_node->line = 1` before invoking a generator.
- `gen_build_args(test_db->ast->root, test_db, NULL, NULL)` creates `struct cil_args_build` for direct calls into `__cil_build_ast_node_helper`.

Generator APIs covered in this chunk include:

- `cil_gen_avrule` negative tail coverage for bad access-vector rule inputs.
- `cil_gen_type_rule` for `CIL_TYPE_TRANSITION`, `CIL_TYPE_CHANGE`, and `CIL_TYPE_MEMBER`.
- User and MLS declarations: `cil_gen_user`, `cil_gen_userlevel`, `cil_gen_userrange`, `cil_gen_sensitivity`, `cil_gen_sensalias`, `cil_gen_category`, `cil_gen_catset`, `cil_gen_catalias`, `cil_gen_catrange`, `cil_gen_catorder`, `cil_gen_dominance`, and `cil_gen_senscat`.
- Role/user/type relation helpers: `cil_gen_roletype`, `cil_gen_userrole`, and `cil_gen_classcommon`.
- Level and range helpers: `cil_fill_level`, `cil_gen_level`, and `cil_gen_levelrange`.
- Constraint and context helpers: `cil_gen_constrain`, `cil_fill_context`, and `cil_gen_context`.
- Labeling/context statements: `cil_gen_filecon`, `cil_gen_portcon`, `cil_fill_ipaddr`, `cil_gen_nodecon`, `cil_gen_genfscon`, `cil_gen_netifcon`, `cil_gen_pirqcon`, `cil_gen_iomemcon`, `cil_gen_ioportcon`, `cil_gen_pcidevicecon`, and `cil_gen_fsuse`.
- Higher-level block-like policy objects: `cil_gen_macro`, `cil_gen_call`, `cil_gen_optional`, `cil_gen_policycap`, and `cil_gen_ipaddr`.
- Whole-builder and dispatcher paths: `cil_build_ast` and the internal `__cil_build_ast_node_helper`.

Important data structures and constants under test include `struct cil_tree`, `struct cil_tree_node`, `struct cil_db`, `struct cil_type_rule`, CIL flavor constants such as `CIL_TYPE_RULE`, `CIL_USER`, and dispatcher keywords, plus result constants `SEPOL_OK` and `SEPOL_ERR`.

## Control Flow

Most direct generator tests follow a consistent flow: construct a token vector for one CIL form, build a parse tree, allocate a `test_ast_node`, initialize a `cil_db`, attach the AST node under `test_db->ast->root`, then call the target generator with the parse-tree node and AST node. Positive tests assert `SEPOL_OK`, the expected `test_ast_node->flavor`, non-null generated data, and specific internal string/list fields. Negative tests assert `SEPOL_ERR`.

The type-rule tests at lines 10236-10773 are representative. Valid `typetransition`, `typechange`, and `typemember` forms are expected to populate `src_str`, `tgt_str`, `obj_str`, `result_str`, set the matching `rule_kind`, and mark the AST node as `CIL_TYPE_RULE`. Each rule kind then has null-current, null-AST, missing source, missing target, missing object class, missing result, and extra-token tests.

The user and MLS sections progressively cover named declarations, aliases, sets, ranges, orders, dominance, and sensitivity/category relationships. Many negative tests deliberately make an operand a nested list where a scalar name is expected, remove required tokens by truncating `next` pointers, or pass anonymous range/level forms with empty lists. `cil_fill_level` and `cil_fill_context` are lower-level fillers: their tests check correct extraction of sensitivity/categories and user/role/type/low/high-level fields from nested parse nodes before the higher-level named generators are tested.

The labeling and low-level context sections validate grammar-specific branching. File contexts are tested for file-type selectors such as directory, file, char, block, socket, pipe, symlink, and any. Port contexts distinguish `udp` and `tcp`, validate single ports and two-value ranges, and reject unknown protocols, malformed ranges, missing ports, and bad contexts. IP address handling is split between `cil_fill_ipaddr` for inline anonymous address parsing and `cil_gen_ipaddr` for named IPv4/IPv6 declarations. Node, genfs, netif, pirq, iomem, ioport, pcidevice, and fsuse tests cover their required identifiers, numeric parsing, optional anonymous contexts, and extra-token rejection.

The macro, call, and optional sections exercise CIL constructs that contain nested bodies or argument lists. Macro tests cover every accepted parameter kind in this chunk (`type`, `role`, `user`, `sensitivity`, `category`, `catset`, `level`, `class`, `classmap`, and `permset`), duplicate handling, unknown parameter kinds, unnamed or empty macros, missing parameter names, and parameter names containing periods. Call tests cover calls with arguments, no arguments, anonymous/list arguments, missing names, and name-in-parentheses errors. Optional tests cover named optional blocks, empty optionals, missing rule bodies, extra tokens, and name-in-parentheses errors.

`cil_build_ast` itself is tested near lines 19522-19583 for the whole tree build path: a simple parse tree should build successfully, while null `db`, null `ast`, null tree, and a malformed subtree should fail. The subsequent dispatcher tests call `__cil_build_ast_node_helper` directly with `struct cil_args_build`. These tests verify keyword-to-generator routing and the `finished` flag. For example, `class`, `common`, `sid`, `sidcontext`, `userlevel`, `userrange`, `rangetransition`, and conditional blocks set `finished = 1` when the helper consumes the node completely, while declarations or container-like forms such as `user`, `type`, `typeattribute`, `block`, `macro`, `call`, `optional`, and several type relationship helpers leave traversal to continue with `finished = 0`.

## State And Persistence Behavior

This is unit-test code only. It does not perform durable filesystem, policy-store, or kernel state changes. State is in-memory CIL parser and AST state:

- `gen_test_tree` creates transient parse trees from token arrays.
- `cil_db_init` creates a temporary CIL database and AST root for symbol-table insertion and parent context.
- Successful generators allocate and attach node-specific data to `test_ast_node->data`, set `test_ast_node->flavor`, and may add named declarations to the parent/root symbol table.
- Lower-level fill helpers populate preallocated CIL objects such as levels, contexts, and IP address structures.
- Some negative tests manually corrupt parse tree links, such as assigning `next = NULL`, to simulate truncated forms.

The chunk generally does not emphasize cleanup. Several tests allocate databases, AST nodes, lists, and parse trees without local destruction, which is common in narrow CUnit parser tests but means the tests are better at validating return/status contracts than ownership balance. The generated AST data persists only for the life of the test process.

## Dependencies And Integration Points

The file includes `CuTest.h`, `CilTest.h`, `test_cil_build_ast.h`, and the production CIL headers `../../src/cil_build_ast.h` and `../../src/cil_tree.h`; it also includes `<sepol/policydb/policydb.h>`. The direct declaration of `__cil_build_ast_node_helper` exposes an internal helper to the test suite, so this chunk is tightly coupled to non-public builder internals and not just the public libsepol CIL API.

The tests integrate with the CIL parser representation through `struct cil_tree_node` sibling/child links (`next`, `cl_head`) and with the AST representation through node flavors, parent pointers, line numbers, and generated datum fields. Dispatcher tests integrate with the AST traversal protocol through `struct cil_args_build`, including the current AST parent, current database, optional macro context, and optional tunable-if stack.

Semantically, this chunk is tied to the CIL language grammar accepted by `cil_build_ast.c`. Changes to syntax for access rules, MLS declarations, contexts, network labels, device labels, macro parameter kinds, optional blocks, or conditional blocks should be reflected here; conversely, failing tests in this chunk usually indicate a parser/builder contract change rather than a runtime policy enforcement issue.

## Risks And Edge Cases

The chunk boundary is itself a review risk. It starts inside one avrule negative test and ends inside a typealias dispatcher negative test, so neither boundary test is fully represented here. The merge/reconciliation lane needs neighboring chunks to avoid treating this range as a complete per-file report.

The tests rely heavily on synthetic parse trees and direct pointer manipulation. That is useful for precise failure paths, but it can differ from real parser output, especially for malformed syntax the lexer/parser might reject before `cil_build_ast.c` sees it. Directly nulling `next` pointers also bypasses normal parse-tree ownership and structural invariants.

Many positive tests validate only selected fields. For example, they often assert flavor and key strings but not complete list contents, symbol-table state, destructor behavior, duplicate handling beyond a targeted case, or later resolver behavior. A generator can pass these tests while still producing an AST that fails in resolution or binary policy emission.

Input validation is broad but grammar-specific. Missing operands, extra operands, scalar-vs-list mismatches, invalid protocol names, malformed IP addresses, and numeric parsing failures are well represented. More semantic conflicts, such as unresolved names, duplicate declarations in broader scopes, MLS ordering consistency, or policy capability validity beyond syntax, are generally handled later in the CIL pipeline and are not fully proven by these tests.

Because the test suite invokes internal helpers and checks implementation-specific flavors and data fields, refactors that preserve public behavior but change internal AST construction may require coordinated test updates. The dispatcher tests in particular are sensitive to the exact `finished` traversal protocol.

## Test Signals

Strong signals from this chunk include:

- Access-vector and type-rule parsers reject null inputs, truncated operands, malformed nested lists, and extra tokens.
- Type transition/change/member rules populate source, target, object, result, rule kind, and `CIL_TYPE_RULE` flavor for valid forms.
- User, user-level, user-range, sensitivity, category, alias, set, and range generators accept valid named and anonymous forms and reject missing names, empty ranges/sets, unexpected lists, and extra tokens.
- Role/type and user/role relation generators reject malformed left/right operands and nested sublists in places that require scalar identifiers.
- Class/common and class-common parsing validates required class/common names and permission lists.
- MLS ordering, dominance, sensitivity/category mapping, level, level-range, and context helpers validate nested low/high level structure.
- Constraint parsing handles direct class/perm forms, class sets, perm sets, and invalid expressions.
- File, port, node, genfs, netif, pirq, iomem, ioport, pcidevice, and fsuse context generators validate object selectors, numeric ranges, contexts, anonymous contexts, and extra-token rejection.
- Macro and call parsing validates parameter kinds, duplicate and malformed parameter declarations, argument lists, and missing names.
- Optional blocks, policy capabilities, and named IP address declarations receive direct positive and negative syntax coverage.
- `cil_build_ast` and `__cil_build_ast_node_helper` tests verify top-level build error propagation and dispatcher routing for many CIL keywords, including expected `finished` behavior.

Useful follow-up coverage would include leak/ownership checks under ASan or valgrind, parser-to-builder integration tests using actual CIL source text rather than synthetic trees, and end-to-end checks that ASTs built by these helpers resolve and emit expected policy structures.

### subset-b-008359: lines 20683-22965

# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_build_ast.c lines 20683-22965

## Chunk Scope

This chunk is the final chunk of `test_cil_build_ast.c`. It starts at the tail of the `typealias` negative test and then covers a large sequence of CUnit tests for `__cil_build_ast_node_helper`, ending with tests for `__cil_build_ast_last_child_helper`. The tested CIL constructs include type attributes, bounds, role statements, AV rules, type transition/change/member rules, booleans/tunables, MLS sensitivities/categories/ranges/levels, constraints, contexts, labeling statements, hardware/resource context statements, macros, calls, optionals, policy capabilities, and IP address declarations.

The chunk does not define production code. It directly exercises static/internal CIL AST-build helpers by declaring local prototypes and by building synthetic parse trees from token arrays.

## Purpose

The tests validate that the AST builder's keyword dispatch path accepts well-formed CIL statements, rejects malformed or context-forbidden statements, and sets the traversal `finished` flag consistently. This is integration-style unit coverage for the internal production flow in `cil_build_ast.c`:

- `__cil_build_ast_node_helper` ignores non-statement parse nodes, checks whether a statement is legal in the current nesting context, dispatches the statement keyword to the matching `cil_gen_*` routine, appends the generated AST node under the current AST parent, and usually asks the tree walker to skip child parsing for leaf statements.
- `__cil_build_ast_last_child_helper` unwinds `struct cil_args_build` state when a subtree is complete, clears context markers such as macro/optional/boolean-if state, and destroys parse-tree children to reduce memory use.

The main value of this chunk is breadth: it provides one positive and one negative signal for many CIL grammar entry points through the common AST-build dispatcher, rather than only testing each `cil_gen_*` routine in isolation.

## Important APIs, Types, And Functions

- `gen_test_tree(&test_tree, line)` converts a NULL-terminated token array into a `struct cil_tree` parse tree. The tests generally call the helper on `test_tree->root->cl_head->cl_head`, meaning the first token inside the first top-level list.
- `cil_db_init(&test_db)` creates a fresh `struct cil_db` with an AST root used as the target parent for generated AST nodes.
- `gen_build_args(test_db->ast->root, test_db, macro, tifstack)` allocates the test-local `struct cil_args_build` wrapper. In this file it contains `ast`, `db`, `macro`, and `tifstack` fields matching the subset needed by these direct helper calls.
- `__cil_build_ast_node_helper(parse_current, &finished, extra_args)` is the central function under test. The tests assert `SEPOL_OK` or `SEPOL_ERR` and check whether `finished` remains `0` or becomes `1` (`CIL_TREE_SKIP_NEXT`).
- `__cil_build_ast_last_child_helper(parse_current, extra_args)` is tested at the end to ensure a normal subtree exit succeeds and a NULL extra-args call is expected by the test to fail.
- `cil_macro_init`, `cil_tree_node_init`, and `cil_destroy_macro` are used by the nested macro negative tests to synthesize a current macro context and verify that statements forbidden inside macros are rejected.
- CUnit assertions are all `CuAssertIntEquals`, so the tests observe return code and traversal state, not detailed AST node contents.

## Control Flow Covered

Each test follows the same pattern: create a tokenized CIL statement, build a parse tree, initialize a database, initialize `finished = 0`, create `extra_args`, call the internal helper, and assert the outcome. Positive tests expect the production dispatcher to route to the appropriate generator:

- `typeattribute`, `typeattributeset`, `userbounds`, `role`, `roletransition`, `roleallow`, `rolebounds`, `roletype`, and `userrole`.
- AV rules: `allow`, `auditallow`, `dontaudit`, and `neverallow`, each using source/target/class/perms syntax.
- Type rules: `typetransition`, `typechange`, and `typemember`.
- Boolean-like statements: `boolean` and `tunable`.
- MLS/MCS primitives: `sensitivity`, `sensitivityalias`, `category`, `categoryset`, `categoryorder`, `categoryalias`, `categoryrange`, `dominance`, `sensitivitycategory`, `level`, and `levelrange`.
- Constraint and context statements: `constrain`, `mlsconstrain`, `context`, `filecon`, `portcon`, `nodecon`, `genfscon`, `netifcon`, `pirqcon`, `iomemcon`, `ioportcon`, `pcidevicecon`, and `fsuse`.
- Higher-level structural statements: `macro`, `call`, `optional`, `policycap`, and `ipaddr`.

The negative tests mutate arity or token shape: missing operands, empty lists, extra operands, identifiers wrapped in lists where atoms are expected, or malformed nested expressions. A few tests invoke statements below later top-level siblings, for example dominance, sensitivitycategory, and level tests select a later `cl_head` via chained `next` pointers after setting up prerequisite sensitivity/category/order declarations in the same parse tree.

The expected `finished` behavior is significant. Leaf-like statements generally expect `finished == 1`, because production code sets `CIL_TREE_SKIP_NEXT` for statements that do not contain nested policy statements. Container-like or declaration paths such as `macro`, `optional`, `role`, `typeattribute`, `boolean`, and `ipaddr` commonly expect `finished == 0` in these tests. Negative cases expect `finished == 0` so failed parses do not request traversal skipping.

## State And Persistence Behavior

All state is in memory. There are no files, policy databases on disk, or persistent artifacts written by these tests. The important transient state is:

- The parse tree produced by `gen_test_tree`.
- The AST rooted at `test_db->ast->root`, which receives nodes if `__cil_build_ast_node_helper` succeeds.
- The `finished` traversal flag passed by pointer.
- The synthetic build context in `struct cil_args_build`, especially `ast`, `db`, and optional `macro`.

Most tests do not destroy `test_tree`, `test_db`, or `extra_args`, which keeps the code short but means the unit binary relies on process teardown for many allocations. The nested macro negative tests are exceptions: they explicitly destroy the database and macro object after checking that nested `macro` and `tunableif` statements are rejected inside macro context.

`__cil_build_ast_last_child_helper` has production-side memory behavior that matters to this chunk: it walks the current AST state back to the parent, clears contextual flags, and calls `cil_tree_children_destroy(parse_current->parent)`. The positive last-child test exercises this path with an `ipaddr` parse subtree.

## Dependencies And Integration Points

This chunk depends on the CIL unit-test harness and libsepol CIL internals:

- `CuTest` and `CilTest.c` register these functions into the CIL build-AST test suite.
- `test_cil_build_ast.h` declares every test in this chunk, including the final `extraargsnull` and last-child tests.
- `../../src/cil_build_ast.h` and direct prototypes expose internal helper behavior to the test file.
- `../../src/cil_tree.h` provides tree-node structures and parse-tree traversal fields such as `cl_head`, `cl_tail`, `next`, and `parent`.
- Production generator functions reached through `parse_statement` include many `cil_gen_*` routines such as `cil_gen_typeattribute`, `cil_gen_avrule`, `cil_gen_typetransition`, `cil_gen_catset`, `cil_gen_constrain`, `cil_gen_context`, `cil_gen_macro`, and `cil_gen_ipaddr`.
- Policy-version and CIL keyword constants are indirectly relevant through `cil_db_init` and the `CIL_KEY_*` keyword dispatch in `cil_build_ast.c`.

The tests are registered near the end of `CilTest.c` in the same rough order as the generator-specific tests, so this chunk acts as final dispatcher coverage after lower-level `cil_gen_*` unit tests.

## Risks And Edge Cases

- The chunk asserts only return code and `finished`; it does not inspect the generated AST node flavor, stored strings, or child structure. A dispatcher could route to the wrong generator but still return `SEPOL_OK` in some cases without this chunk detecting it.
- Several tests depend on exact parse-tree navigation such as `root->cl_head->next->next...`. These are brittle if `gen_test_tree` changes tree shape or if fixture setup inserts/removes top-level forms.
- Many allocations are not cleaned up in ordinary tests. That is acceptable for short-lived CUnit processes but weakens leak-detection usefulness unless the broader harness resets or tolerates these allocations.
- The NULL `extra_args` tests are important risk signals. The production helper implementation dereferences `extra_args` through `args` early in both node-helper and last-child-helper flows; if there is no defensive check in the compiled path, these tests may crash rather than cleanly returning `SEPOL_ERR`. This should be reconciled against the actual build configuration and any wrapper behavior.
- Some positive tests use placeholder identifiers such as `con`, `context`, `low`, and `high` without requiring full semantic resolution. They validate AST construction syntax, not later name resolution or policy validity.
- The `roleallow` positive token array lacks a closing `")"` token in this chunk, yet expects success. That suggests this direct helper test cares only about the current statement's immediate parse node and may not detect malformed outer list completion.
- Nested macro negative tests manually fabricate a `CIL_MACRO` node as context. That is effective for `check_for_illegal_statement`, but it does not simulate every field a real macro AST node would carry.

## Test Signals

Strong signals in this chunk:

- Positive/negative coverage pairs for a broad range of CIL keywords through the shared AST-build helper.
- Validation that malformed arity and malformed list/atom shape return `SEPOL_ERR` without setting `finished`.
- Validation that list-valued constructs such as type attribute sets, category sets/orders/ranges, MLS levels, constraints, contexts, and network/interface contexts request child traversal skipping once parsed.
- Validation that context restrictions reject nested `macro` and `tunableif` statements when `extra_args->macro` is active.
- Validation that last-child handling succeeds for a normal AST state and is intended to reject NULL extra-args input.

Gaps to consider when using this chunk as a regression signal:

- It does not verify AST contents after insertion.
- It does not check log messages or error specificity.
- It does not execute a full `cil_build_ast` traversal over the whole parse tree for these statements; most tests call the node helper directly.
- It does not cover later semantic passes such as symbol resolution, MLS range validation, policy capability support checks, or final policydb conversion.
