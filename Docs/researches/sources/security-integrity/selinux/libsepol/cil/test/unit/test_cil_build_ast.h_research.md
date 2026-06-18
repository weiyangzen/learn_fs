# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_build_ast.h

## Purpose
This header is the public declaration surface for the CIL build-AST unit tests. It does not implement logic itself; it exposes hundreds of `CuTest` entry points used by `CilTest.c` to register parser-list conversion, CIL datum generation, AST traversal, and negative validation tests for `libsepol/cil` internals.

## Important APIs, Types, And Functions
The only external type used directly is `CuTest` from `CuTest.h`. All declarations are `void test_...(CuTest *)` functions. The declared surface groups around `cil_parse_to_list`, `cil_set_to_list`, datum generators such as `cil_gen_block`, `cil_gen_class`, `cil_gen_type`, `cil_gen_context`, `cil_gen_filecon`, `cil_gen_portcon`, `cil_gen_nodecon`, `cil_gen_macro`, `cil_gen_call`, `cil_gen_optional`, and AST helper tests such as `test_cil_build_ast_node_helper_*` and `test_cil_build_ast_last_child_helper`.

## Control Flow
Control flow is indirect. `CilTest.c` includes this header, creates a CuTest suite, and registers selected declarations with `SUITE_ADD_TEST`. At runtime each registered function builds synthetic CIL token/list trees, invokes the corresponding CIL generator or AST helper, and asserts `SEPOL_OK` or `SEPOL_ERR`.

## State And Persistence
The header owns no runtime state and has no persistence behavior. Its state impact is compile-time: it defines which test functions other translation units may call. Because the implementations exercise mutable `cil_db`, AST nodes, symbol tables, and generated CIL datums, stale or missing declarations can break suite wiring even though the header stores nothing itself.

## Dependencies And Integration Points
It depends only on `CuTest.h` but names tests for internals implemented in `test_cil_build_ast.c` and registered mainly in `CilTest.c` under the build suite. It is tightly coupled to private CIL parser/build APIs because the implementation reaches functions such as CIL generators and AST helper paths rather than public libsepol APIs.

## Risks
The header is very broad and manually maintained, so declaration drift is a risk when tests are renamed or removed. Many negative-case declarations encode expected parser arity and shape validation; changing CIL grammar or AST node flavors requires synchronized updates to implementation and suite registration. The size of the declaration list also makes missing registrations easy to overlook.

## Test Signals
Positive signals include broad coverage of grammar constructs, context/range/IP parsing, macro/call/optional constructs, and top-level `cil_build_ast` error handling. Negative signals are especially strong for null arguments, missing operands, sublists where atoms are expected, extra operands, invalid protocols/classes, and duplicate or malformed AST helper cases.
