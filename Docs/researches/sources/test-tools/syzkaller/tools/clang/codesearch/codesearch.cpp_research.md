<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/codesearch/codesearch.cpp -->
# sources/test-tools/syzkaller/tools/clang/codesearch/codesearch.cpp

## Purpose

Clang LibTooling AST indexer that produces a kernel source database for syzkaller agentic codesearch.

## Important APIs, Types, and Functions

Classes `Instance`, `PPCallbacksTracker`, `IndexerAstConsumer`, `Indexer`, `NamedDeclEmitter`, `ScopedState`; visitors for functions, globals, records, enums, typedefs, calls, decl refs, member refs, and type refs.

## Control Flow

Constructor dispatches to `Main` when `SYZ_RUN_CLANGTOOL=codesearch`; `ClangTool` traverses each translation unit, opens definition contexts with body/comment ranges, records calls/uses/read-write/address references and record layouts, then emits JSON.

## State and Persistence Behavior

State is per-process `Output`, current definition pointer, source manager, callee/type-reference flags, and AST traversal context; persistence is stdout consumed by Go indexing.

## Dependencies and Integration Points

Depends on Clang/LLVM tooling, compilation database, and local `json.h`/`output.h`; integrated by `tools/syz-codesearch` and `pkg/codesearch`.

## Risks and Edge Cases

Macro source ranges can cross files and are clamped; macro recording is stubbed; anonymous/duplicate names and simple parent-based write detection limit precision.

## Test Signals

Golden C fixtures for calls, callback arrays, comments, static globals, typedef/struct uses, field reads/writes, macro-generated declarations.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/codesearch/codesearch.cpp -->
