# sources/test-tools/syzkaller/pkg/compiler/check.go

Purpose: Semantic validation engine for syzlang ASTs. It performs phased checks before and after constants are patched, including names, type arguments, field paths, resource usability, recursion, varlen placement, attributes, and unused declarations.

Important APIs/types/functions: `typecheck`, `check`, `checkComments`, `checkDirectives`, `checkNames`, `checkFlags`, `checkFields`, `checkTypedefs`, `checkTypes`, `checkTypeValues`, `checkAttributeValues`, `checkFieldPaths`, `CollectUnused`, `CollectUnusedConsts`, `collectUnused`, `collectUsed`, `checkConstructors`, `checkRecursion`, `checkStruct`, `checkCall`, `checkType`, `replaceTypedef`, `instantiate`, `checkTypeArg`, `checkVarlens`, and `checkDupConsts`.

Control flow: `typecheck` handles syntax-adjacent semantics and basic type validity. `check` runs after constants are available and validates values, attributes, unused nodes, recursive layouts, constructor/input reachability, varlen rules, and const/flag conflicts. Typedef handling can instantiate template structs into synthetic AST nodes. Field-path validation resolves `len`, `bytesize`, `offsetof`, and `value(...)` paths through syscall arguments, parents, structs, and nested fields.

State and persistence behavior: Mutates compiler in-memory maps (`resources`, `typedefs`, `structs`, flags, used maps, generated template structs, errors/warnings). No disk persistence. Unsupported/broken typedef state prevents duplicate exponential errors.

Dependencies/integration points: Central to `Compile` in `compiler.go`; uses `ast`, `prog`, and `targets`. `CollectUnused` APIs are exported for other tooling.

Risks: Complex recursive traversal must avoid infinite loops through optional pointers, varlen arrays, templates, and parent paths. Field path checks intentionally limit `parent` depth. `checkDupConsts` is disabled due to false positives. Some TODOs mention incomplete transitive unsupported pruning.

Test signals: Extensive coverage through compiler `errors*.txt`, `warnings.txt`, `all.txt`, fuzz seeds, `CollectUnused` tests, flag flattening tests, and full sys description compilation.
