## sources/test-tools/syzkaller/pkg/kfuzztest/builder.go

Purpose: converts extracted KFuzzTest functions, structs, constraints, and annotations into formatted syzlang descriptions.

Important APIs/types/functions: `Builder`, `NewBuilder`, `EmitSyzlangDescription`, `syzStructToSyzlang`, `syzFieldToSyzLang`, `processConstraint`, `processAnnotation`, `resolvesToPtr`, `syzFuncToSyzlang`, and `dwarfToSyzlangType`.

Control flow: builds maps by input type/field, emits struct definitions, emits one `syz_kfuzztest_run$NAME` pseudo-syscall per target, parses/formats through syzkaller AST to normalize output. Field processing lets annotations override DWARF type conversion; constraints are appended only for unannotated fields.

State and persistence: in-memory string generation only.

Dependencies and integration: depends on `debug/dwarf` type shapes and `pkg/ast` parser/formatter. Consumed by `kfuzztest.go`.

Risks: unsupported DWARF types/qualifiers fail generation. `ExpectNe` is ignored due syzlang limitations. Some constraints for `ExpectGt`/`ExpectGe` emit single values rather than open ranges, which may be intentional but narrow. Annotation errors can block all description generation.

Test signals: `description_generation_test.go` compiles C metadata fixtures and compares generated descriptions.
