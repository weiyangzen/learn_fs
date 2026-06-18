<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-codesearch/codesearch.go -->
# sources/test-tools/syzkaller/tools/syz-codesearch/codesearch.go

## Purpose

CLI for building/querying the Clang-based kernel codesearch database.

## Important APIs, Types, and Functions

Flags database/kernel-src/kernel-obj; `index` command via `clangtool.Run[codesearch.Database]`; query dispatch through `codesearch.NewIndex().Command`.

## Control Flow

Index mode runs Clang tool and writes database; query mode opens database with source roots, executes registered command, writes result stdout; usage lists commands/arity.

## State and Persistence Behavior

Persists database on index; query mode read-only except stdout.

## Dependencies and Integration Points

Depends on compilation database, LLVM/cgo clangtool, and `pkg/codesearch` schema.

## Risks and Edge Cases

Indexing is expensive; database schema changes require rebuild; command validation is delegated.

## Test Signals

Tiny compile database index plus every registered command valid/invalid arity.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-codesearch/codesearch.go -->
