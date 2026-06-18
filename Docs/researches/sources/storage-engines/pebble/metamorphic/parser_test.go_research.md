<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/parser_test.go -->
## sources/storage-engines/pebble/metamorphic/parser_test.go

Purpose: verifies that the metamorphic operation parser accepts the textual format used by generated and persisted operation streams and round-trips back through `formatOps`.

Important APIs and functions: `TestParser` runs datadriven `parse` commands over `testdata/parser` using `TestkeysKeyFormat` formatted key and suffix parsers. `TestParserRandom` generates 10,000 operations under both default and multi-instance configs and checks parsed operations equal the generated operations. `TestParserNilBounds` specifically verifies that formatting and parsing an iterator with nil lower/upper bounds preserves nil rather than converting them to empty byte slices.

Control flow: datadriven inputs are parsed with formatted testkey parsing; errors are returned as test output to lock down diagnostics. The randomized test builds a `keyManager`, random generator, operation sequence, formats it, parses it with default parser options, and uses `require.Equal` on operation structs.

State and persistence: the tests are in-memory. They exercise parser object-state tracking indirectly through generated operation sequences containing DBs, batches, iterators, snapshots, and multi-instance object IDs.

Dependencies and integration: depends on `datadriven`, `randvar.NewRand`, `newGenerator`, `multiInstanceConfig`, `DefaultOpConfig`, and `TestkeysKeyFormat`. This makes it an integration test between generation, formatting, parser construction, object-ID utilities, and derived-field computation.

Risks and gaps: randomized coverage is strong for generated legal operations but does not independently fuzz malformed syntax or every compatibility path. Datadriven coverage is only as broad as `testdata/parser`.

Test signals: the file itself is the primary parser test signal, especially the equality round-trip and nil-bound regression.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/parser_test.go -->
