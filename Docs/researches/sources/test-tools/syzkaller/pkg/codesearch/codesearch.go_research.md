# sources/test-tools/syzkaller/pkg/codesearch/codesearch.go

Purpose: Query layer over a source-code entity database for syzkaller's codesearch tool and LLM-facing workflows. It exposes commands for source tree navigation, bounded file reading, definitions, comments, references, and struct/union layouts.

Important APIs/types/functions: `Index`, `Command`, `Commands`, `IsSourceFile`, `NewIndex`, `NewTestIndex`, `Index.Command`, `Entity`, `FileIndex`, `EntityInfo`, `DefinitionComment`, `DefinitionSource`, `ReferenceInfo`, `FindReferences`, `findDefinition`, `GetStructLayout`, `formatSource`, `formatSourceFile`, `escaping`, `dirIndex`, `DirIndex`, and `ReadFile`.

Control flow: Commands validate argument counts through `Index.Command`, call helper methods, and format human-readable output. `FileIndex` first calls `ReadFile` to distinguish empty definition sets from missing files. `definitionSource` resolves an entity by context-aware name lookup and formats either body or comment range. `FindReferences` resolves target definitions, filters by source prefix and reference kind/entity kind/static visibility, optionally formats bounded context snippets, and enforces an output limit while still reporting total count.

State and persistence behavior: `Index` holds an in-memory `Database` loaded from JSON and a list of source directories. There is no mutation after construction. Source reads are bounded: `ReadFile` clamps line count to 1..100, and `FindReferences` clamps context lines to 10000.

Dependencies/integration points: Uses `codesearch.Database` records produced by clangtool, `tooltest.LoadOutput` for tests, `aflow.BadCallError` for user-facing bad tool calls, and `osutil` for filesystem helpers. It supports both source and generated/build directories through `srcDirs`.

Risks: `escaping` rejects cleaned paths containing `..`, which is conservative but string-based. `FindReferences` has a TODO for static symbol ambiguity across files. `GetStructLayout` treats a byte offset as matching a field when `targetBits <= offset+size`, so exact end-boundary semantics should be reviewed for off-by-one expectations. Command output is plain text and part of golden tests.

Test signals: `codesearch_test.go` runs every query fixture and ensures every registered command is covered. Golden fixtures exercise directory listing, reading, definitions, comments, references, and struct layouts.
