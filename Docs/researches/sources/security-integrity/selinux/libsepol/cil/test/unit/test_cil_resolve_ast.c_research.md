# Research: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_resolve_ast.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-008361`: lines 1-10745, `Docs/researches/chunks/subset-b-008361_research.md`
- `subset-b-008362`: lines 10746-17523, `Docs/researches/chunks/subset-b-008362_research.md`

## Chunk Research

### subset-b-008361: lines 1-10745

# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_resolve_ast.c lines 1-10745

## Purpose

This chunk is the first large section of the CIL AST resolver unit-test file for SELinux `libsepol`. It exercises the internal resolver layer that turns parser/build-AST string references into concrete `cil_*` datum pointers and validates pass-specific resolver behavior for blocks, macros, MLS declarations, type enforcement constructs, contexts, network/file labels, and early macro call expansion.

The file is test code, not production resolver logic. Each test builds a small tokenized CIL policy snippet with `gen_test_tree`, initializes a fresh `struct cil_db`, calls `cil_build_ast`, invokes one resolver function or a small sequence of resolver passes, and asserts the expected `SEPOL_OK`, `SEPOL_ENOENT`, or `SEPOL_ERR` result with CuTest. The covered range starts with shared test scaffolding and ends in the beginning of the `cil_resolve_call2_*` tests; the remaining call2/helper-dispatch coverage is in the next chunk.

## Important APIs, Types, And Functions

- `gen_resolve_args()` allocates and populates a local copy of the resolver argument struct used by the internal resolver helpers. The struct fields mirror `cil_resolve_ast.c` internals: `db`, `pass`, `changed`, `callstack`, `optstack`, and `macro`.
- The file forward-declares non-public resolver helpers, especially `__cil_resolve_ast_node_helper()` and `__cil_disable_children_helper()`, because this unit suite reaches into private implementation details through included internal headers.
- Core fixture APIs are `gen_test_tree`, `cil_db_init`, and `cil_build_ast`. Tests depend on the built AST layout and navigate nodes through `test_db->ast->root->cl_head`, `next`, and `cl_head` chains rather than using named lookup helpers.
- Name and top-level resolution coverage includes `cil_resolve_name`, `cil_resolve_ast`, `cil_resolve_roleallow`, `cil_resolve_rolebounds`, `cil_resolve_sensalias`, `cil_resolve_catalias`, `cil_resolve_catorder`, and `cil_resolve_dominance`.
- MLS category/sensitivity/level coverage includes `cil_resolve_cat_list`, `cil_resolve_catset`, `cil_resolve_catrange`, `cil_resolve_senscat`, `cil_resolve_level`, and `cil_resolve_levelrange`, with support calls to `__cil_verify_order` and in some cases `cil_tree_walk`.
- Constraint and context coverage includes `cil_resolve_constrain`, `cil_resolve_context`, and context use through `sidcontext`, `filecon`, `portcon`, `genfscon`, `nodecon`, `netifcon`, `pirqcon`, `iomemcon`, `ioportcon`, `pcidevicecon`, and `fsuse`.
- Type-enforcement coverage includes `cil_resolve_typeattributeset`, `cil_resolve_typealias`, `cil_resolve_typebounds`, `cil_resolve_typepermissive`, `cil_resolve_nametypetransition`, `cil_resolve_rangetransition`, `cil_resolve_classcommon`, `cil_resolve_classpermset`, `cil_resolve_avrule`, and `cil_resolve_type_rule`.
- Namespacing and macro expansion coverage includes `cil_resolve_blockinherit`, `cil_resolve_in`, `cil_resolve_call1`, and the start of `cil_resolve_call2`.
- The tests exercise many CIL data types by casting AST node `data`: `struct cil_typealias`, `cil_catset`, `cil_catrange`, `cil_level`, `cil_levelrange`, `cil_context`, `cil_classmapping`, `cil_classpermset`, `cil_call`, `cil_macro`, `cil_param`, and `cil_list_item`.

## Control Flow

The dominant test pattern is:

1. Define `char *line[]` as a flat token stream representing a small CIL S-expression program.
2. Build a parse tree with `gen_test_tree(&test_tree, line)`.
3. Initialize `struct cil_db *test_db` with `cil_db_init`.
4. Allocate resolver arguments with the pass needed for the resolver under test, commonly `CIL_PASS_MISC1`, `CIL_PASS_MLS`, `CIL_PASS_MISC2`, `CIL_PASS_MISC3`, `CIL_PASS_CALL1`, or `CIL_PASS_CALL2`.
5. Convert the parse tree to an AST via `cil_build_ast(test_db, test_tree->root, test_db->ast->root)`.
6. Navigate to the specific AST node, often through positional `cl_head->next` chains.
7. Call the target resolver and assert its return code.

Several tests intentionally model multi-pass resolver dependencies. Category and sensitivity ordering tests run `cil_resolve_catorder`, `cil_resolve_dominance`, or `cil_tree_walk(..., __cil_resolve_ast_node_helper, ...)` before resolving category ranges, sensitivity/category declarations, or levels. Context and range tests often resolve `senscat`, named `level`, or named `levelrange` data before resolving objects that reference them. Macro tests run `cil_resolve_call1` to bind call arguments to macro parameters, then `cil_resolve_call2` to copy or instantiate macro bodies, and only then resolve constructs inside the call body with `args->callstack` pointing at the call node.

Negative tests alter one missing or malformed reference at a time. Examples include absent source/target roles for `roleallow`, missing classmap names or classpermissionsets for `classmapping`, out-of-order or unknown categories in ranges, missing sensitivities or categories in MLS expressions, unknown users/roles/types in contexts, missing class/permission/type names in TE rules, invalid IP address strings, IPv4/IPv6 family mismatches, and call argument count/flavor mismatches. Return-code distinctions are significant: unresolved names generally expect `SEPOL_ENOENT`, malformed internal state or semantic ordering failures often expect `SEPOL_ERR`, and valid repeated/idempotent resolutions usually expect `SEPOL_OK`.

## State And Persistence Behavior

The tests create only in-memory parser trees, CIL databases, AST nodes, symbol tables, and resolver lists. There is no durable persistence, filesystem I/O, or external policy store interaction in this chunk. Persistent state in the production sense is represented by mutations inside `struct cil_db` and its AST:

- `cil_build_ast` populates `test_db->ast`, symbols, declarations, and node data from the test token stream.
- Resolver calls mutate AST datum pointers, resolved lists, macro/call fields, and ordered lists such as `test_db->catorder` and `test_db->dominance`.
- `changed` is passed by pointer in the resolver argument bundle but is usually only initialized and not asserted in this chunk.
- Some tests intentionally mutate resolver-owned state to trigger error paths, for example trimming `test_db->catorder`, changing a macro parameter flavor, freeing and nulling a call's `macro_str`, or resolving the same bounds declaration twice.

The tests do not consistently free `test_tree`, `test_db`, or `args`; this is typical short-lived unit-test fixture behavior but means memory-leak checks would need either fixture cleanup elsewhere or suppressions for intentional test lifetime allocations.

## Dependencies And Integration Points

- Depends on SELinux/libsepol public policydb definitions through `<sepol/policydb/policydb.h>`.
- Depends on CuTest through `CuTest.h` and local CIL test utilities through `CilTest.h`.
- Reaches into CIL internals by including `../../src/cil_build_ast.h`, `../../src/cil_resolve_ast.h`, `../../src/cil_verify.h`, and `../../src/cil_internal.h`.
- Integrates with the CIL pass model. Tests explicitly select pass constants and therefore document which resolver routines are expected to run in which compiler phase.
- Integrates with symbol-table lookup behavior through `cil_resolve_name` and CIL symbol spaces such as `CIL_SYM_TYPES` and `CIL_SYM_BLOCKS`.
- Integrates with macro/block expansion semantics through `cil_resolve_blockinherit`, `cil_resolve_in`, `cil_resolve_call1`, `cil_resolve_call2`, `callstack`, and macro parameter/call argument flavor checks.
- Integrates with MLS ordering validation through `__cil_verify_order`, `test_db->catorder`, and `test_db->dominance`.
- The token streams exercise CIL language surface forms: `block`, `macro`, `call`, `in`, `class`, `common`, `classmap`, `classmapping`, `permissionset`, `classpermissionset`, `allow`, `typetransition`, `typechange`, `typemember`, `rangetransition`, `context`, `sidcontext`, and labeling forms.

## Coverage By Area

- Lines 1-142 establish includes, private helper declarations, `struct cil_args_resolve`, `gen_resolve_args`, baseline `cil_resolve_name` success/failure tests, and a null-root `cil_resolve_ast` failure.
- Lines 143-561 cover role and classmapping resolution, including anonymous/named classpermissionsets and macro-contained classmapping arguments.
- Lines 562-1818 cover MLS aliases, category/sensitivity order, category lists/sets/ranges, and sensitivity-category expressions, including named categorysets, nested ranges, order verification, and missing-name failures.
- Lines 1819-2700 cover level and levelrange resolution for named and anonymous levels, including category list/categoryset inputs and missing sensitivity/category/range endpoints.
- Lines 2701-3598 cover constraint expressions, context resolution, macro-supplied levelranges, named ranges, missing user/role/type/range parts, and roletransition lookup.
- Lines 3599-4202 cover typeattributeset expression resolution, type aliases, type bounds, typepermissive declarations, name type transitions, and expected duplicate/unknown-target behavior.
- Lines 4203-5663 cover rangetransition variants, including named ranges, anonymous ranges, macro-supplied levels/ranges, missing type/class/level references, and anonymous low/high level failures.
- Lines 5664-6296 cover class/common binding, named/anonymous classpermissionsets, permission sets, and AV rule resolution with missing source/target types, classes, permissions, and named permission sets.
- Lines 6297-6725 cover `typetransition`, `typechange`, and `typemember` through the shared `cil_resolve_type_rule` path, checking source type, target type, object class, and result type lookups.
- Lines 6726-9070 cover object, filesystem, network, and hardware labeling resolvers: `filecon`, `portcon`, `genfscon`, `nodecon`, `netifcon`, `pirqcon`, `iomemcon`, `ioportcon`, `pcidevicecon`, `fsuse`, and `sidcontext`. Tests check named and anonymous contexts, IPv4/IPv6 handling, missing context references, and invalid embedded context fields.
- Lines 9071-9218 cover `blockinherit` and `in` resolution for blocks, macros, and optionals.
- Lines 9219-10745 cover `cil_resolve_call1` for many parameter flavors: no-parameter calls, type, role, user, sensitivity, category, categoryset, level, ipaddr, class, classmap, permissionset, and classpermissionset parameters. It includes anonymous argument forms, malformed anonymous structures, unknown macro names, extra/missing arguments, duplicate copied names, and forced parameter-flavor corruption. The chunk then begins `cil_resolve_call2` success tests for type, role, user, sensitivity, category, categoryset, permissionset, and classpermissionset parameters.

## Risks And Edge Cases

- The tests use positional AST navigation heavily. Any AST child ordering change in `cil_build_ast` can break tests even if resolver semantics remain correct.
- The local `struct cil_args_resolve` duplicate and private helper declarations make this suite sensitive to internal resolver implementation changes that are not exposed through a stable public header.
- Many fixtures depend on exact pass sequencing. A production pass reorder or a resolver being moved between pass phases could require coordinated updates across many tests.
- Return-code expectations encode subtle distinctions between name-not-found and malformed-state errors. Regressions can be hidden if a resolver returns a generic failure code that still causes policy compilation to fail but no longer preserves diagnostic specificity.
- Macro tests are high-risk because they rely on `callstack`, argument flavor, named-vs-anonymous parameter conversion, and two-stage call resolution. Bugs here can cause references to resolve in the wrong namespace or copied macro bodies to retain stale parameter state.
- MLS tests stress category/sensitivity ordering; incorrect order list mutation can cause later ranges or sensitivity-category expressions to succeed with invalid dominance/category semantics.
- Network label tests cover IPv4/IPv6 family agreement and anonymous IP address parsing. Missing these cases could allow malformed CIL to progress into lower policydb layers.
- Anonymous context tests validate recursive resolution of inline contexts. If anonymous context parsing changes, failures may surface across file, port, genfs, node, hardware, fsuse, and sidcontext resolver paths.
- Some tests deliberately modify internals after partial resolution. These are valuable for error-path coverage but can become brittle when data ownership or initialization changes.

## Test Signals

- A healthy run should compile this file with access to internal CIL headers and execute each `test_cil_resolve_*` CuTest case in the suite registration that appears later in the file.
- Positive resolver tests should return `SEPOL_OK` for valid CIL snippets, including repeated/idempotent cases such as duplicate category/dominance resolution calls and repeated level resolution.
- Missing declaration tests should return `SEPOL_ENOENT`, especially for unresolved users, roles, types, classes, permissions, categories, sensitivities, contexts, macro names, block names, and named ranges.
- Malformed semantic-state tests should return `SEPOL_ERR`, including invalid range ordering, mismatched IP families, malformed anonymous arguments, extra or missing macro call arguments, and manually corrupted parameter flavor data.
- Macro-related tests should be run with both `CIL_PASS_CALL1` and `CIL_PASS_CALL2` paths because call1 validates/binds arguments while call2 begins copying or materializing macro content. Later chunks complete that call2 coverage.
- Changes to `cil_resolve_ast.c`, `cil_build_ast.c`, CIL AST node ordering, CIL pass constants, macro parameter flavors, or MLS ordering helpers should be validated against this suite because this chunk is broad regression coverage for resolver internals.

### subset-b-008362: lines 10746-17523

# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_resolve_ast.c lines 10746-17523

## Scope And Purpose

This chunk is a large unit-test band for libsepol CIL AST resolution. It does not implement resolver behavior directly; it constructs small CIL token streams, builds ASTs from them, drives specific resolver entry points, and asserts the expected `SEPOL_OK`, `SEPOL_ERR`, or `SEPOL_ENOENT` outcomes.

The covered tests exercise these resolver areas:

- macro call second-pass argument binding and call argument lookup;
- boolean and tunable expression resolution and evaluation;
- user/role/type/MLS relationship resolution;
- disabling AST subtrees for optional or inactive declarations;
- the generic `__cil_resolve_ast_node_helper` dispatcher across many CIL statement flavors;
- resolver error behavior for missing symbols, wrong symbol flavors, null inputs, invalid pass/flavor combinations, callstack/optional-stack constraints, and unresolved optional content.

The tests are source-tree-aligned with the CIL resolver internals, especially the multi-pass resolver model where different declarations are resolved in `CIL_PASS_CALL1`, `CIL_PASS_CALL2`, `CIL_PASS_MISC1`, `CIL_PASS_MISC2`, `CIL_PASS_MISC3`, `CIL_PASS_TIF`, and `CIL_PASS_BLKIN`.

## Important APIs, Types, And Functions

The common test setup uses `gen_test_tree` to transform a string-token array into a `struct cil_tree`, `cil_db_init` to create a fresh `struct cil_db`, `cil_build_ast` to populate `test_db->ast->root`, and `gen_resolve_args` to create `struct cil_args_resolve` with a pass, change flag, callstack, optional stack, and extra resolver context.

Macro resolution is tested through `cil_resolve_call1`, `cil_resolve_call2`, and `cil_resolve_name_call_args`. These tests cover formal/actual argument binding for classes, classmaps, levels, IP addresses, anonymous levels/IP addresses, wrong flavors, missing names, missing argument lists, null call pointers, and null names.

Expression resolution and evaluation are tested through `cil_resolve_expr_stack`, `cil_resolve_boolif`, `cil_resolve_tunif`, and `cil_evaluate_expr_stack`. The expression tests cover booleans, tunables, types, roles, users, unary `not`, binary operators `and`, `or`, `xor`, `eq`, `neq`, nested operator placement on either operand side, missing symbols, and malformed conditional nodes with null strings.

Relationship-specific resolver APIs include `cil_resolve_userbounds`, `cil_resolve_roletype`, `cil_resolve_userrole`, `cil_resolve_userlevel`, `cil_resolve_userrange`, and `cil_resolve_senscat`. These verify user/role/type linkage and MLS level/range resolution, including named levels/ranges, anonymous MLS syntax, and macro-substituted level or range arguments.

Subtree state behavior is tested through `__cil_disable_children_helper`, which is invoked on optional blocks, blocks, users, roles, types, aliases, common/class declarations, booleans, sensitivities, categories, category sets, SIDs, macros, contexts, levels, policy capabilities, permissions, category/sensitivity aliases, tunables, and unknown/unhandled flavors.

The generic resolver dispatch path is tested through `__cil_resolve_ast_node_helper`. This section covers call resolution, conditionals, category ordering, dominance, role allow rules, aliases, category sets/ranges, levels/ranges, constraints, contexts, sensitivity-category mappings, role transitions, type attributes and aliases, bounds, permissive types, range transitions, named type transitions, AV rules, type rules, user relationships, context-bearing labeling rules, hardware/resource context statements, block inheritance, class-common links, optional/macro/call stack handling, and negative guard paths.

Key CIL data structures appearing directly in the tests include `struct cil_db`, `struct cil_tree`, `struct cil_tree_node`, `struct cil_args_resolve`, `struct cil_call`, `struct cil_args`, `struct cil_booleanif`, `struct cil_tunableif`, `struct cil_constrain`, `struct cil_conditional`, `struct cil_optional`, and `struct cil_symtab_datum`.

## Control Flow

Most tests follow a fixed pattern:

1. Define a compact CIL policy fragment as a `char *line[]` token array.
2. Build a parse tree and AST with `gen_test_tree`, `cil_db_init`, and `cil_build_ast`.
3. Create resolver arguments with the appropriate pass.
4. Select an AST node by walking `test_db->ast->root->cl_head`/`next`/`cl_head` links.
5. Invoke a focused resolver function or the generic helper.
6. Assert the resolver return code with `CuAssertIntEquals`.

The macro-call tests model the two-pass call flow explicitly. `cil_resolve_call1` locates and validates the macro call target and records call metadata. The test then switches `args->pass` to `CIL_PASS_CALL2` and invokes `cil_resolve_call2` to bind actual arguments to macro parameters. Later lookup tests call `cil_resolve_name_call_args` after those passes to validate that macro-local names resolve to the correct actual AST nodes and flavors.

Expression tests first resolve symbol names in expression stacks, then evaluate tunable expression stacks where appropriate. Boolean conditionals use `CIL_PASS_MISC1`; tunable conditionals use `CIL_PASS_TIF`; constraint expressions involving user/role/type symbols use `CIL_PASS_MISC3`. Negative cases distinguish missing symbols (`SEPOL_ENOENT`) from malformed resolver inputs (`SEPOL_ERR`).

MLS user-level and user-range tests show the dependency between passes. They resolve `sensitivitycategory` relations in `CIL_PASS_MISC2` using `cil_resolve_senscat`, then switch to `CIL_PASS_MISC3` before resolving `userlevel` or `userrange`. Macro variants add `CIL_PASS_CALL1` and `CIL_PASS_CALL2` before MLS resolution and set `args->callstack` when resolving statements inside expanded macro call content.

`__cil_resolve_ast_node_helper` acts as a dispatcher keyed by `node->flavor` and `args->pass`. The tests confirm that the helper invokes the correct specialized resolver for each pass/flavor pair, leaves `finished` as `0` for these unit paths, and tolerates stack states for calls, optionals, disabled optionals, and macros where expected.

## State And Persistence Behavior

The tests are entirely in-memory. They create transient `struct cil_db` and AST instances and do not persist policy output, write files, update repository state, or create compiled SELinux policy artifacts.

The important state transitions are resolver-internal:

- `cil_build_ast` attaches typed CIL data to AST nodes and populates symbol tables used by later resolution.
- `cil_resolve_call1` and `cil_resolve_call2` mutate call-related structures so macro formal parameters can map to actual arguments and nested macro statements can be resolved against `args->callstack`.
- `cil_resolve_expr_stack` replaces or annotates expression-stack conditionals with resolved symbol references and validates their expected flavors.
- `cil_evaluate_expr_stack` reads resolved tunable values and computes a boolean result.
- `cil_resolve_tunif` can mark branches active/inactive according to evaluated tunable conditions.
- `__cil_disable_children_helper` walks AST subtrees and changes `cil_symtab_datum.state` or related declaration state to disabled where appropriate.
- `__cil_resolve_ast_node_helper` relies on `args->optional`/optional stack and callstack state to decide whether failures should propagate normally, be converted into optional-disable behavior, or be rejected as invalid nesting.

Because each test initializes a new database, there is no cross-test persistence. However, these tests are persistence-relevant for the compiler as a whole: successful resolution determines which declarations and rules survive into later CIL compilation and policy emission.

## Dependencies And Integration Points

The chunk depends on the CUnit/CuTest harness through `CuTest` and `CuAssertIntEquals`. It also depends on local test helpers defined elsewhere in `test_cil_resolve_ast.c`, including `gen_test_tree` and `gen_resolve_args`.

The resolver APIs under test are integration points between the AST builder, symbol tables, macro expansion/call handling, conditional expression logic, MLS model resolution, optional block semantics, and the broader libsepol CIL compilation pipeline.

The CIL language constructs used in token streams include `class`, `common`, `classcommon`, `classmap`, `classmapping`, `macro`, `call`, `allow`, `boolean`, `booleanif`, `tunable`, `tunableif`, `category`, `categoryorder`, `sensitivity`, `sensitivitycategory`, `sensitivityalias`, `categoryalias`, `categoryset`, `categoryrange`, `level`, `levelrange`, `context`, `constrain`, `mlsconstrain`, `user`, `role`, `type`, `userbounds`, `rolebounds`, `typebounds`, `roletype`, `userrole`, `userlevel`, `userrange`, `roleallow`, `roletransition`, `typeattributeset`, `typealias`, `typepermissive`, `rangetransition`, `typetransition`, `typechange`, `typemember`, `filecon`, `portcon`, `genfscon`, `nodecon`, `netifcon`, `pirqcon`, `iomemcon`, `ioportcon`, `pcidevicecon`, `fsuse`, `sid`, `sidcontext`, `block`, `blockinherit`, and `optional`.

Return-code expectations integrate with libsepol's public error vocabulary. `SEPOL_OK` indicates successful resolution, `SEPOL_ENOENT` indicates a referenced declaration was not found or a dependent symbol failed to resolve, and `SEPOL_ERR` indicates malformed input, invalid resolver context, incompatible flavors, or illegal stack/pass combinations.

## Risks And Edge Cases

The tests rely heavily on positional AST navigation such as `root->cl_head->next->next`. This is concise but fragile: adding declarations to a test token stream or changing AST construction order can point a test at the wrong node while still compiling.

Several negative tests intentionally corrupt internals after AST construction, such as changing a macro argument flavor to `CIL_SYM_UNKNOWN`, nulling a conditional string, using an empty user string in `sidcontext`, or passing null call/name/helper arguments. These are valuable guard tests, but they depend on internal structure layouts and can become stale if the implementation refactors data ownership.

Macro argument tests cover many flavors, but they mainly assert return codes rather than inspecting the exact resolved nodes. A resolver regression that returns `SEPOL_OK` while binding to an incorrect but compatible datum could escape these tests unless later compilation fails.

MLS tests rely on correct pass sequencing. Missing the `CIL_PASS_MISC2` sensitivity-category resolution step before `CIL_PASS_MISC3` userlevel/userrange resolution can turn otherwise valid fragments into `SEPOL_ENOENT`. This mirrors production pass ordering and makes these tests good signals for pass-regression bugs.

Optional behavior is subtle. The helper can treat some failures inside optionals as non-fatal by disabling optional content, but it rejects invalid optional stack combinations for tunables and macro call resolution. Changes around `args->optional`, disabled state, or "failed to resolve" handling have high regression risk.

The generic AST helper tests cover broad flavor dispatch but usually assert only the top-level return code and `finished == 0`. They do not fully validate all side effects, such as final datum pointers, list contents, branch enablement, or disabled child states.

Context-bearing rule tests are security-sensitive because incorrect resolution of contexts, MLS ranges, IP addresses, netmasks, filesystems, ports, devices, or SIDs can produce incorrect SELinux labeling rules. The negative tests catch unresolved references but not every semantic validation rule.

## Test Signals

Direct signals in this chunk include:

- `test_cil_resolve_call2_*` validates macro call second-pass handling for classes, classmaps, levels, anonymous levels, IP addresses, anonymous IP addresses, unknown flavors, and missing argument syntax.
- `test_cil_resolve_name_call_args*` validates successful and failing call-argument name lookup across flavor mismatches, null inputs, absent call args, and unresolved names.
- `test_cil_resolve_expr_stack_*`, `test_cil_resolve_boolif*`, `test_cil_resolve_tunif*`, and `test_cil_evaluate_expr_stack_*` validate expression name resolution, boolean/tunable branch resolution, and operator evaluation.
- `test_cil_resolve_userbounds*`, `test_cil_resolve_roletype*`, `test_cil_resolve_userrole*`, `test_cil_resolve_userlevel*`, and `test_cil_resolve_userrange*` validate user/role/type and MLS relationship resolution, including macro and anonymous MLS forms.
- `test_cil_disable_children_helper_*` validates that the disable helper handles many AST flavors without error and respects already-disabled optionals.
- `test_cil_resolve_ast_node_helper_*` validates dispatch for specialized resolver functions over call, conditional, MLS, access-rule, transition, context, device, filesystem, block, class-common, rolebounds, optional, macro, and invalid-input paths.

Useful follow-up coverage would inspect resolved datum pointers and state transitions after successful calls, add tests for deeply nested macro/optional combinations, and verify complete side effects for context-bearing statements rather than relying only on return codes.
