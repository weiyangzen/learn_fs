# sources/test-tools/syzkaller/pkg/compiler/compiler.go

Purpose: Top-level syzlang compiler orchestration. It converts parsed AST descriptions and constants into `prog` resources, syscalls, and types.

Important APIs/types/functions: `Prog`, `createCompiler`, `Compile`, `compiler`, `error`, `warning`, `filterArch`, `structIsVarlen`, `parseIntAttrs`, `parseAttrs`, `parseAttrExprArg`, `parseAttrIntArg`, `parseAttrStringArg`, `getTypeDesc`, `getArgsBase`, `derefPointers`, `foreachType`, `foreachSubType`, `removeOpt`, `parseIntType`, `flattenFlags`, `flattenIntFlags`, `flattenStrFlags`, and `recurFlattenFlags`.

Control flow: `Compile` clones the AST, prepends built-ins, filters nodes by file metadata/target arch, typechecks, flattens nested flags, either extracts constants or assigns syscall numbers, patches constants, runs full semantic checks, generates syscalls/resources/types, lays out types, and emits warnings. If any phase records errors, compilation stops.

State and persistence behavior: All compiler state is in-memory. Returned `Prog.Unsupported` persists unsupported syscall/flag information to callers. If `consts == nil`, `Prog.fileConsts` is used internally by `ExtractConsts`.

Dependencies/integration points: Integrates `pkg/ast`, `prog`, and `sys/targets`. Called by sysgen, extraction tooling, tests, and fuzzing. It relies on helpers defined across `attrs.go`, `check.go`, `consts.go`, `gen.go`, `meta.go`, and `types.go`.

Risks: Phase ordering is critical; later checks assume type argument counts are valid. `structIsVarlen` caches before fully traversing recursive structures to avoid hangs. Flag flattening has a hard cap of 100000 values.

Test signals: Exercised by full target compilation in `compiler_test.go`, canned testdata, const extraction tests, and fuzzing.
