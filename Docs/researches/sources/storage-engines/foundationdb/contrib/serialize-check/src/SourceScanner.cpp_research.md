# sources/storage-engines/foundationdb/contrib/serialize-check/src/SourceScanner.cpp

## Purpose
`SourceScanner.cpp` is a Clang LibTooling executable that scans C++ source files for FDBRPC-style serializable classes. For each matching class, it emits one JSON object on stdout containing the class name, source file path, declaration line, member variables, and raw body of the `serialize` method.

## Important APIs, Types, And Functions
- `SerializableClassInfo` is the result model. It stores `className`, `sourceFilePath`, `lineNumber`, `variables`, and `rawSerializeCode`.
- `SerializableClassInfo::SerializableClassMemberVariable` stores `name` and `type` for each field.
- `operator<<` pretty-prints class info for humans, though the main path uses JSON.
- `toJson(const SerializableClassInfo&)` uses Boost.JSON to serialize class info, including a `variables` array and `raw` serialize body.
- `serializableClassMatcher` is the central AST matcher. It matches `cxxRecordDecl` nodes that have a function template with a template type parameter bound as `archiverType`, and a `serialize` method with one parameter bound as `archiver` and compound body bound as `serializeFuncBody`.
- `SerializableClassMemberVariableCollector` is a `RecursiveASTVisitor` that visits `FieldDecl` nodes and appends field name/type pairs to the current class info.
- `SerializableClassMatchCallback` handles matches. It validates that the template type name equals the serialize parameter's non-reference type string, initializes class metadata from the source manager, collects fields, extracts raw serialize body source text, and writes JSON to stdout.
- `tryParseSerializeFuncBody` extracts source text for the compound statement body using `getBeginLoc`, `getEndLoc`, `Lexer::getLocForEndOfToken`, and `SourceManager::getCharacterData`.
- `getSerializableClassMatchFinder()` creates a `MatchFinder`, registers the matcher under `traverse(TK_IgnoreUnlessSpelledInSource, ...)`, and intentionally leaks the match finder and callback for process lifetime.
- `main` uses `CommonOptionsParser::create`, constructs `ClangTool`, and runs a frontend action factory built from the match finder.

## Control Flow
The executable receives normal Clang Tooling arguments, typically `source_scanner [-p compilation_database] path_to_source_code`. `main` parses options, creates a `ClangTool` for requested source paths, and runs the match finder. For each matched class declaration, the callback validates the archiver parameter type, fills a result structure, recursively visits the record declaration for member fields, extracts serialize body text, and prints one JSON line. `renormalize.py` consumes these JSON lines in parallel across many source files.

## State And Persistence Behavior
The scanner has no persistent state and does not write files. `knownClasses` is declared globally but unused. The match finder is intentionally heap-allocated and leaked until process exit. All output is streaming JSON to stdout; parse errors and Clang diagnostics flow through normal Clang Tooling channels/stderr.

## Dependencies And Integration Points
The scanner depends on Boost.JSON and Clang/LLVM libraries: AST, AST matchers, frontend, serialization, and tooling. Its build target is declared in the sibling CMake file. It integrates with FoundationDB serialization conventions by looking for templated `serialize` methods where the method parameter type matches the template parameter (usually `template <class Ar> void serialize(Ar& ar)`). The Python driver expects output fields named `className`, `sourceFilePath`, `lineNumber`, `variables`, and `raw`.

## Risks And Edge Cases
- The matcher identifies records with a templated `serialize` method, but does not verify return type, access level, method constness, specific `serializer(...)` calls, or FDB-specific archive semantics.
- `checkParameterType` compares stringified template names to `getNonReferenceType().getAsString()`. This is brittle across aliases, qualified names, `const`, pointers, forwarding references, and Clang formatting differences. A stronger AST type identity check would be more robust.
- The commented `isReferenceable` check notes LLVM-version limitations; reference validation is currently incomplete.
- `tryParseSerializeFuncBody` assumes begin/end character pointers are in a comparable buffer after selecting the compound statement. Macro-heavy or generated code can still make source extraction fragile.
- Field collection traverses the whole record declaration and may include fields from nested declarations or implementation details depending on AST shape. It does not filter static fields, inherited fields, or access specifiers explicitly.
- Anonymous records or classes without a normal declaration name produce empty `className`.
- `operator<<` writes variable details to `std::cout` rather than the provided stream for those lines, which would be surprising if the operator were used in the JSON path.
- `knownClasses` is unused, suggesting either incomplete deduplication or leftover implementation.
- The intentional leak is acceptable for a short-lived CLI but would be inappropriate in a long-running library or daemon.

## Test Signals
Good fixtures should compile tiny C++ files with matching and non-matching serialize patterns: correct `template <class Ar> void serialize(Ar& ar)`, wrong parameter count, wrong parameter type, non-template serialize, macro-decorated serialize, nested classes, inherited fields, static fields, anonymous records, and serialize declarations without bodies. Tests should assert valid line-delimited JSON, stable `sourceFilePath`/line numbers, accurate field lists and type strings, and raw body extraction. Integration tests should run through `renormalize.py` to ensure JSON schema compatibility.
