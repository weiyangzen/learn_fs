# sources/test-tools/syzkaller/pkg/aflow/tool/codesearcher/codesearcher.go

## Purpose
Wraps syzkaller's clang-based kernel code search index as aflow tools for file entity lists, comments, source definitions, references, and struct layouts.

## Important APIs, Types, and Functions
Exports `ToolFileIndex`, `ToolDefinitionComment`, `ToolDefinitionSource`, `ToolFindReferences`, `ToolStructLayout`, `Tools`, and `PrepareIndex`. `prepare` builds or reuses a cached clangtool index keyed by kernel commit/config/database hash. The private `index` wrapper prevents full JSON marshaling/unmarshaling of the index object.

## Control Flow
`prepare` calls `ctx.Cache`, runs clangtool if needed, then opens `codesearch.NewIndex` over source/object roots. Tool functions forward arguments into the index and translate result structs. `findReferences` chooses output limits based on snippet context size.

## State and Persistence Behavior
Index state is cached under aflow cache storage and intentionally not serialized into journals. Tool calls are read-only over kernel source/index files.

## Dependencies and Integration Points
Depends on `aflow`, `clangtool`, `pkg/codesearch`, `pkg/hash`, and `tools/clang/codesearch`. Integrated by codeexpert and source-inspection agents.

## Risks and Test Signals
Risks include stale cache keys, huge reference output, and accidental index serialization. Tests in `codesearcher_test.go` cover struct layout success/error; broader integration depends on clangtool index generation.
