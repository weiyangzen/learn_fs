# sources/storage-engines/foundationdb/bindings/ruby/lib/fdbtuple.rb

Purpose: This module implements the Ruby FoundationDB tuple layer, preserving sortable binary encoding for common Ruby values.

Important APIs and types: Public surface includes `FDB::Tuple.pack`, `unpack`, `range`, `compare`, `UUID`, and `SingleFloat`. It supports nil, binary/ASCII strings, UTF-8 strings, integers, booleans, single and double floats, UUIDs, and nested arrays.

Control flow: `encode` dispatches by Ruby class and string encoding, escapes null bytes, encodes variable-length integers, adjusts floats for lexicographic order, and recursively encodes arrays. `decode` parses type codes and reconstructs Ruby values. `compare` orders tuples element-by-element using type codes and special float comparison.

State and persistence behavior: The module is stateless except class variables for constants and size limits. Its packed bytes are persistent keys, so compatibility with other bindings is critical.

Dependencies and integration points: It is required by `fdbsubspace`, `fdbdirectory`, and `tester.rb`. It must remain compatible with Python and other binding tuple layers.

Risks: Ruby string encodings distinguish bytes and UTF-8 strings, so callers must force binary where needed. Versionstamp support is absent here compared with the Python tuple layer. Float edge cases and integer bounds are compatibility-sensitive.

Test signals: Ruby tester tuple operations pack/unpack/sort/range values and encode/decode floats. Cross-binding tester comparisons validate ordering and binary compatibility for supported types.
