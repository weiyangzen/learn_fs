<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/declextract/output.h -->
# sources/test-tools/syzkaller/tools/clang/declextract/output.h

## Purpose

JSON schema for declextract output, covering C types, constants, structs/enums, functions/scopes, syscalls, file ops, ioctls, io_uring, and netlink.

## Important APIs, Types, and Functions

Variant `FieldType` with `IntType`, `PtrType`, `ArrType`, `BufferType`, struct name; records `Struct`, `Enum`, `Function`, `Syscall`, `FileOps`, `Ioctl`, `NetlinkPolicy`, `TypingFact`; `Output::emit/print`; `TodoType`.

## Control Flow

Extractor callbacks build typed records and push them into category vectors; print emits fixed top-level arrays through `JSONPrinter`.

## State and Persistence Behavior

All state is owned by `Output` vectors and `unique_ptr` variant fields; no direct file writes.

## Dependencies and Integration Points

The JSON field names are a contract with downstream Go consumers and generated syzlang tooling.

## Risks and Edge Cases

Default/empty `FieldType` can be unsafe if printed without a branch; schema changes need synchronized consumers.

## Test Signals

Golden JSON for each record type, optional elem fields, TODO type, and nested typing facts.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/declextract/output.h -->
