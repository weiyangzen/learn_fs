# sources/object-store/minio-mc/cmd/cat-main.go

## Purpose

`cat-main.go` implements `mc cat`, streaming object, file, zip member, versioned, or stdin content to stdout with range/tail support and terminal-safe output.

## Important APIs, Types, and Functions

`catFlags` includes rewind, version-id, zip, offset, tail, and part-number. `prettyStdout` replaces non-printable runes with `^?` for terminals. `catOpts` stores parsed options. `parseCatSyntax`, `catURL`, `catOut`, and `mainCat` are the core flow.

## Control Flow

The handler creates a cancellable context, validates encryption keys, parses syntax and incompatible flags, handles stdin, preserves argument order when `-` is present, then streams each URL. `catURL` stats remote/local content to determine size, version ID, and tail offset, opens a source stream with `GetOptions`, and calls `catOut`. `catOut` copies to stdout or `prettyStdout`, handles broken pipes gracefully, and verifies the byte count when expected size is known.

## State and Persistence Behavior

The command reads object/file/stdin data and writes stdout only. It does not modify source objects. It may read encrypted object metadata and version information through stat/get paths.

## Dependencies and Integration Points

It integrates with encryption key validation, `url2Stat`, `getSourceStreamFromURL`, `GetOptions`, rewind parsing, object versioning, zip extraction support, terminal detection, and typed client errors such as `UnexpectedEOF`.

## Risks and Edge Cases

`checkCatSyntax` requires at least one arg, making `stdinMode` in `parseCatSyntax` unreachable unless call structure changes. `prettyStdout` preserves invalid UTF-8 replacement runes but masks control characters. Tail/offset/part-number combinations are carefully rejected. Size verification is disabled for part downloads and unknown sizes.

## Test Signals

Tests should cover pretty stdout, incompatible flags, rewind versus version ID, tail offset calculation, offset beyond object size, broken pipe handling, stdin `-` ordering, and encrypted/versioned object options.
