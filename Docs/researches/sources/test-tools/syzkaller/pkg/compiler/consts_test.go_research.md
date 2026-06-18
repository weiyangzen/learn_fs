# sources/test-tools/syzkaller/pkg/compiler/consts_test.go

Purpose: Tests for syzlang constant extraction and const extraction diagnostics.

Important APIs/types/functions: `TestExtractConsts` and `TestConstErrors`.

Control flow: `TestExtractConsts` parses `testdata/consts.txt`, extracts constants for Linux/amd64, and compares expected constant names, includes, incdirs, and defines. `TestConstErrors` parses `consts_errors.txt`, runs extraction, and checks expected diagnostics through `ast.ErrorMatcher`.

State and persistence behavior: Reads testdata only. No writes.

Dependencies/integration points: Exercises `ast.Parse`, `ExtractConsts`, target metadata, and compiler error handling.

Risks: Expected const list is explicit and must be updated with fixture changes. Diagnostics are phase-sensitive.

Test signals: Validates const discovery in syscall numbers, type arguments, defines, includes, incdirs, and error paths.
