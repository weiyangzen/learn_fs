# sources/test-tools/syzkaller/pkg/compiler/compiler_test.go

Purpose: Core test suite for the syzlang compiler.

Important APIs/types/functions: `TestCompileAll`, `TestData`, `TestAutoConsts`, `TestFuzz`, `TestAlign`, `TestCollectUnusedError`, `TestCollectUnused`, `TestFlattenFlags`, and `TestSquashablePtr`.

Control flow: `TestCompileAll` parses every `sys/<os>/*.txt`, loads const files, and compiles for every target arch. `TestData` runs phase-specific canned inputs and expected errors/warnings. Other tests cover auto const files, fuzz regression seeds, recursive alignment, unused collection, nested flag flattening, and pointer squashing decisions.

State and persistence behavior: Reads sys descriptions, const files, and testdata. With `-update`, it can rewrite formatted `all.txt`. Otherwise no persistent writes.

Dependencies/integration points: Exercises `ast`, `serializer`, `prog`, `targets`, `DeserializeConstFile`, `ExtractConsts`, `FabricateSyscallConsts`, `Compile`, and `CollectUnused`.

Risks: `TestCompileAll` is broad and can be costly because it spans all OS/arch descriptions. The formatting update flag can rewrite source testdata. Some assertions inspect generated `prog.Type` details, so serializer/type layout changes can require updates.

Test signals: Very strong integration signal for parser, const extraction, semantic checking, code generation, target-specific constants, warnings, and regression fuzz seeds.
