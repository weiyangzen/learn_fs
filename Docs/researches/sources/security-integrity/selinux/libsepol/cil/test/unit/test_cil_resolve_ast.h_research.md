# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_resolve_ast.h

Purpose: Declares the CuTest test surface for CIL AST/name resolution. It is not implementation code; it is the registration contract for a very broad set of resolver unit tests.

Important APIs and functions: The header exports prototypes for `test_cil_resolve_name`, `test_cil_resolve_ast_curr_null_neg`, resolver cases for role/type/user/MLS/category/class/permission constructs, `call`, `boolif`, `tunif`, context/net/file object contexts, expression-stack evaluation, optional disabling, and many `__cil_resolve_ast_node_helper` paths. Each test takes `CuTest *`.

Control flow: No executable flow exists here. The unit-test runner includes this header, binds the declared functions into suites, and the implementations construct CIL AST fixtures and assert resolver return codes.

State and persistence: The header owns no state. Test implementations exercise transient CIL databases, AST nodes, symbol tables, macro/call stacks, optional stacks, and resolved datum pointers.

Dependencies and integration points: Includes `CuTest.h`; pairs with CIL unit-test implementation files and internal resolver code under `cil/src`.

Risks: Because this header is a large manual declaration list, duplicate or missing prototypes can silently hide unregistered coverage. It has a duplicated `test_cil_resolve_call1_level` and repeated userlevel helper prototypes, signaling historical drift.

Test signals: Successful CIL unit-test build, suite registration for every prototype, and negative tests returning expected resolver errors are the validation signals.
