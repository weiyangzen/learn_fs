# sources/test-tools/syzkaller/executor/_include/flatbuffers/registry.h

## Purpose

`registry.h` defines `flatbuffers::Registry`, a convenience class for converting arbitrary FlatBuffers to text and text back to binary by looking up schemas from file identifiers.

## Important APIs, Types, and Functions

Public methods are `Register`, `FlatBufferToText`, `TextToFlatBuffer`, `SetOptions`, `AddIncludeDirectory`, and `GetLastError`. Private `LoadSchema` resolves an identifier to a schema path, loads schema text, configures a `Parser`, and parses it. State includes `lasterror_`, `opts_`, `include_paths_`, and `schemas_`.

## Control Flow

Callers register schemas by file identifier. `FlatBufferToText` checks minimum buffer length, extracts the identifier bytes after the root offset, loads the matching schema, then calls `GenText`. `TextToFlatBuffer` loads a schema by supplied identifier, parses text through `Parser::Parse`, and returns `parser.builder_.Release()`. `LoadSchema` handles unknown identifiers, load failure, parse failure, options, and include paths.

## State and Persistence Behavior

The registry stores schema paths and include-directory pointers, but does not cache schema text or parsed schemas. Each conversion creates a local parser. `lasterror_` stores the latest failure. `DetachedBuffer` owns successful binary output.

## Dependencies and Integration Points

It includes `base.h` and `idl.h`, using `LoadFile`, `Parser`, `IDLOptions`, `GenText`, `DetachedBuffer`, and file identifier constants. It is useful for tools that accept multiple schema families.

## Risks and Edge Cases

Identifiers are raw four-byte values and may not be printable. `include_paths_` stores raw `const char *`, so pointed strings must outlive the registry. Reparse-on-every-call can be expensive. Buffer-to-text rejects buffers shorter than `sizeof(uoffset_t) + kFileIdentifierLength`.

## Test Signals

Tests should register multiple schemas, convert binary to text, parse text back to binary, validate include directories, and assert errors for truncation, unknown identifiers, missing schema files, schema parse errors, and text parse errors.
