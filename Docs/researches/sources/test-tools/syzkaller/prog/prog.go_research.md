## sources/test-tools/syzkaller/prog/prog.go

Purpose: defines the core in-memory program representation: programs, calls, argument implementations, resource links, mutation-safe replacement/removal helpers, sanitization, and human-readable argument formatting.

Important APIs/types/functions: `Prog`, `CallProps`, `Call`, `MakeCall`, `Arg`, `ArgCommon`, `ConstArg`, `PointerArg`, `DataArg`, `GroupArg`, `UnionArg`, `ResultArg`, constructors for each arg kind, `InnerArg`, `replaceArg`, `replaceResultArg`, `removeArg`, `RemoveCall`, `FormatArg`, `sanitize`, and `CallProps.ForeachProp`.

Control flow: constructors assign type refs and directions. Replacement copies concrete arg data while repairing resource use maps. Removing an arg walks all subargs, deletes incoming resource links, and resets users to defaults. `RemoveCall` removes all call arguments and return values before slicing the call list. `FormatArg` recursively renders structured args.

State and persistence: owns mutable in-memory program state. `ResultArg.uses` is the main internal cross-link structure. `Prog.isUnsafe` relaxes validation for special data-mmap programs.

Dependencies/integration: used by all generation, mutation, serialization, validation, minimization, and execution encoding paths.

Risks: any shallow copy or missed resource-link update can corrupt the graph. `replaceArg` has special structure-preserving behavior for structs but allows array length changes. `DataArg` clones input data on construction/set to avoid accidental aliasing.

Test signals: `prog_test.go`, `mutation_test.go`, validation, serialization, and fuzz tests exercise constructors, clone stability, defaults, special structs, and cross-target serialization.
