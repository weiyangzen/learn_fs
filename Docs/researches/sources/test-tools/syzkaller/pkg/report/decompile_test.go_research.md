# sources/test-tools/syzkaller/pkg/report/decompile_test.go

Purpose: Tests parsing of objdump text output into `DecompiledOpcode` records.

Important test: `TestParseObjdumpOutput` feeds a synthetic binary disassembly with offsets 0, 1, 2, 4, and 9, including a `(bad)` instruction, then compares the parsed slice to expected offsets, instruction strings, `IsBad`, and full descriptions.

Control flow and state: Calls only `objdumpParseOutput`; it does not invoke external objdump or create temp files.

Dependencies and integration: Protects the parser used by `DecompileOpcodes` and report opcode decompilation paths.

Risks: Does not cover architecture argument building, command timeouts, unsupported architectures, empty-output error handling, or multiline/variant objdump formats.

Test signals: Focused guard for regex parsing and bad-instruction classification.
