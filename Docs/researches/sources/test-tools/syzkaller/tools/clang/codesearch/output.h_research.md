<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/codesearch/output.h -->
# sources/test-tools/syzkaller/tools/clang/codesearch/output.h

## Purpose

JSON schema and output accumulator for the Clang codesearch indexer.

## Important APIs, Types, and Functions

Defines entity/ref kind constants, `LineRange`, `Reference`, `FieldInfo`, `Definition`, `print` overloads, and `Output::emit/print`.

## Control Flow

AST traversal appends `Definition` records with ranges, refs, and field layout; `Output::print` emits top-level JSON `definitions` through `JSONPrinter`.

## State and Persistence Behavior

In-memory `std::vector<Definition>` only; writes to stdout via printer.

## Dependencies and Integration Points

Consumed by Go `pkg/codesearch` and agentic codesearch tools, so field names are API surface.

## Risks and Edge Cases

Schema renames are compatibility breaks; reference kinds are intentionally coarse; anonymous field/record names can collide.

## Test Signals

Golden JSON for every entity/ref kind, comments, static globals, empty refs, and field offsets/sizes.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/codesearch/output.h -->
