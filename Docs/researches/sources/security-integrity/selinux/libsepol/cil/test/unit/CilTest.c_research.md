# sources/security-integrity/selinux/libsepol/cil/test/unit/CilTest.c

## Purpose
`CilTest.c` is the central CIL test-suite registry and shared fixture helper file. It collects tests from many `test_cil_*` modules into CuTest suites for base utilities, AST build behavior, AST resolve behavior, copy/post behavior, and full integration.

## Important APIs, Types, And Functions
Shared helpers include `set_cil_file_data()` and `gen_test_tree()`. `set_cil_file_data()` reads `test/policy.cil` into a newly allocated `struct cil_file_data` buffer with two trailing NUL bytes. `gen_test_tree()` builds a simple `struct cil_tree` from a NULL-terminated token array, interpreting `"("` as descent into a new parse node, `")"` as ascent, and other tokens as parse-node data strings.

Local tests `test_symtab_init()` and `test_symtab_init_no_table_neg()` directly exercise `symtab_init()` using `cil_sym_sizes`. Suite factories are `CilTreeGetResolveSuite()`, `CilTreeGetBuildSuite()`, `CilTreeGetSuite()`, and `CilTestFullCil()`. The file contains 1,583 `SUITE_ADD_TEST` registrations, making it the authoritative map from test functions in included headers to executable CuTest suites.

## Control Flow
Each suite factory creates a `CuSuite` with `CuSuiteNew()`, registers test functions with `SUITE_ADD_TEST`, and returns the suite. `CilTreeGetResolveSuite()` focuses on name resolution, expression evaluation, optional/macro/call handling, conditionals, constraints, MLS structures, contexts, labeling, networking, hardware contexts, filesystem use, and symbol resolution negative paths. `CilTreeGetBuildSuite()` focuses on parsing/building AST nodes from syntax, including malformed input cases. `CilTreeGetSuite()` focuses on lower-level utilities, copy helpers, post-sort comparators, lexer/parser/FQN/list/tree/symtab behavior, and common copy regressions. `CilTestFullCil()` registers `test_min_policy` and `test_integration`.

## State And Persistence
The file allocates memory for helper structures and suites but does not persist test data. `set_cil_file_data()` depends on the current working directory containing `test/policy.cil`. `gen_test_tree()` allocates tree nodes and duplicated strings for tests to consume.

## Dependencies And Integration Points
The file includes CuTest, CIL internals, libsepol policydb headers, and a broad set of local test headers such as `test_cil_tree.h`, `test_cil_list.h`, `test_cil_symtab.h`, `test_cil_parser.h`, `test_cil_lexer.h`, `test_cil_build_ast.h`, `test_cil_resolve_ast.h`, `test_cil_fqn.h`, `test_cil_copy_ast.h`, `test_cil_post.h`, and `test_integration.h`. It is consumed by `AllTests.c`.

## Risks
The registry is manually maintained. A test function can exist but never run if it is omitted, commented out, or hidden behind a stale include. The high number of registrations makes merge conflicts and accidental duplicate/missing tests likely. `set_cil_file_data()` exits the process on file/stat/read errors, which is direct but prevents normal CuTest failure reporting. Several tests are commented out, documenting known gaps in negative/error-path coverage.

## Test Signals
The file itself is the primary test signal for CIL coverage breadth. It includes positive and negative cases for AST construction, resolution, macro expansion, conditionals, constraints, contexts, access-vector rules, MLS categories and levels, network and filesystem contexts, copy behavior, and post-processing comparators. Coverage is broad but depends on `AllTests.c` running the suites and on consumers checking stdout failures.
