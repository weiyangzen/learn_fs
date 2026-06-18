<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/json.h -->
# sources/test-tools/syzkaller/tools/clang/json.h

## Purpose

Minimal streaming JSON printer used by the C++ Clang tools.

## Important APIs, Types, and Functions

`JSONPrinter`, RAII `Scope`, string escaping, scalar/string/vector/pointer `Field` overloads, and free `print` overload dispatch for complex types.

## Control Flow

Callers open scopes and write fields; printer handles commas, nesting, vectors, optional pointers, and escaped strings to stdout.

## State and Persistence Behavior

Printer formatting state only; no parsed data ownership or file persistence.

## Dependencies and Integration Points

Included by both Clang output schemas instead of an external JSON dependency.

## Risks and Edge Cases

Correctness depends on caller `last` flags and matching `print` overloads; it is an emitter only, not a validator/parser.

## Test Signals

Golden output with escaping, empty vectors, nested objects, optional pointers, and comma boundaries.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/json.h -->
