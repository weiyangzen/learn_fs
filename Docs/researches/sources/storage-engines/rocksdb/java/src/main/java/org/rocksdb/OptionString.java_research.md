# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/OptionString.java research

## Purpose

`OptionString` parses RocksDB-style option strings into structured key/value entries for Java mutable option builders. It supports simple scalar/list values and nested complex values wrapped in braces.

## Important APIs and types

`Value` holds either `List<String>` or `List<Entry>`, with `isList()`, `fromList()`, `fromComplex()`, and `toString()`. `Entry` stores a key and `Value`. `Parser.parse(String)` returns a list of top-level entries or throws `Parser.Exception`, a runtime exception with context around the parse position.

## Control flow

The parser keeps a mutable `StringBuilder` of unconsumed input. It skips whitespace, parses keys from alphanumeric/underscore characters, requires `=`, then parses either complex `{...}` values or list-like simple values separated by `:`. Complex values are sequences of options separated by `;`. After top-level parsing, leftover input is an error.

## State and persistence behavior

Parser state is local and transient. Parsed entries feed builders that can produce mutable option payloads; any persistence effect comes from applying those options to RocksDB.

## Dependencies and integration points

It depends only on Java collections and `Objects`. It is used by `MutableDBOptions.parse()` and `MutableColumnFamilyOptions.parse()`.

## Risks and test signals

The grammar is intentionally narrow: keys cannot include dots, values have limited character support, braces serve both complex and wrapped simple values, and escaping is minimal. Tests should cover whitespace, empty embedded vectors, complex values, wrapped values, list separators, malformed input context, and round-trips with mutable option builders.
