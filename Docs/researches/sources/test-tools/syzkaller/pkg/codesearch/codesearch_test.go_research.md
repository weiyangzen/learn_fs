# sources/test-tools/syzkaller/pkg/codesearch/codesearch_test.go

Purpose: Golden tests for the codesearch clang extraction and query command layer.

Important APIs/types/functions: `TestClangTool`, `TestCommands`, and `testCommand`.

Control flow: `TestClangTool` delegates to `tooltest.TestClangTool[Database]` with the compiled codesearch clang tool. `TestCommands` loads a merged test index from `testdata`, finds `query*` fixture files, and runs each query. `testCommand` parses the first line into command plus arguments, executes `Index.Command`, converts expected bad-call errors into output text, and compares the result against the whole fixture file.

State and persistence behavior: Uses fixture files and golden `.json` databases. The `covered` map tracks which commands were exercised and fails if any command lacks a query fixture.

Dependencies/integration points: Integrates `clangtool/tooltest`, `osutil`, and the C++ tool package imported as `tools/clang/codesearch`.

Risks: The first-line parser only supports whitespace-separated args with simple surrounding quotes, not escaped spaces or complex shell syntax. Golden output tightly couples user-facing command text to tests.

Test signals: Provides full command registry coverage and validates clang database output against expected JSON for all test C files.
