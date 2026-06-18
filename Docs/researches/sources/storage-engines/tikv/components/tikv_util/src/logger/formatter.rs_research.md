# sources/storage-engines/tikv/components/tikv_util/src/logger/formatter.rs

## Purpose
Provides low-level formatting helpers for TiKV's unified text log format: source file name sanitization and conditional JSON escaping of log tokens.

## Important APIs, Types, And Functions
`write_file_name` writes only ASCII alphanumeric, dot, dash, and underscore bytes from a filename. `write_escaped_str` writes a value directly unless `need_json_encode` detects bytes that must be JSON encoded according to TiKV's unified log format.

## Control Flow
`write_file_name` scans byte ranges and writes contiguous allowed segments while skipping disallowed bytes. `need_json_encode` returns true for control/space bytes through `0x20`, double quote, equals, left bracket, or right bracket. `write_escaped_str` either writes raw UTF-8 bytes or delegates to `serde_json::to_writer`.

## State And Persistence
No state or persistence; all functions stream to the caller-provided writer.

## Dependencies And Integration
Depends on `std::io` and `serde_json`. It is used by `logger/mod.rs` when writing source file, message, key, and value fields in text logs.

## Risks
The escaping predicate is byte-oriented by design; non-ASCII characters are allowed raw unless combined with a byte requiring JSON encoding. `write_file_name` silently strips disallowed characters, which is useful for log safety but can make unusual filenames less identifiable.

## Test Signals
Tests cover escaping decisions for ASCII, spaces, separators, controls, replacement/Unicode text, and mixed Unicode with spaces. Filename tests verify disallowed punctuation, controls, whitespace, and non-ASCII characters are stripped while safe filename characters remain.
