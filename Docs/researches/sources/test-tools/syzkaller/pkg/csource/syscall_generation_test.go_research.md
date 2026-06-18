# sources/test-tools/syzkaller/pkg/csource/syscall_generation_test.go

This file snapshot-tests syscall expression and generated argument comments against files under `pkg/csource/testdata`. It is focused on exact formatting, not full C compilation.

Important types are `testData` and `annotatedCall`. `TestGenerateSyscalls` reads test cases, creates a Linux/amd64 target, and compares generated comments and `fmtCallBody` output to checked-in expectations. A `-update` flag rewrites testdata when generation intentionally changes. `readTestCases` and `readTestData` parse each fixture as input program lines up to a blank line followed by repeated comment blocks and syscall expression lines. `testGenerationImpl` deserializes the program, formats comments through `Format`, serializes/deserializes exec form, and compares each generated syscall body.

State and persistence are limited to optional fixture rewriting when `-update` is set. Dependencies include clang-format through `Format`, Linux/amd64 target metadata, `prog` parsing, and exact comment prefix conventions from `csource.go`.

Risks include brittle textual comparisons, formatter availability, testdata parser assumptions about blank lines and comment prefixes, and broad fixture rewrites hiding unintended changes. Test signal is precise: failures pinpoint changes in argument annotation, resource formatting, native syscall names, constants/flags, and pointer/value rendering.
