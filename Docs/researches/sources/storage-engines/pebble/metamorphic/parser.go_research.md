<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/parser.go -->
## sources/storage-engines/pebble/metamorphic/parser.go

Purpose: implements the text parser for Pebble metamorphic test operations. The textual operation format is intentionally Go-like, allowing `go/scanner` and `go/token` to tokenize operation logs produced by `formatOps` and `op.String()`.

Important APIs and types: `parse(src, parserOpts)` is the entry point. `parserOpts` provides formatted user-key/suffix parsers and an `allowUndefinedObjs` compatibility mode. `methodInfo`, `makeMethod`, the `methods` map, and `opArgs` define the grammar binding between operation names, valid receiver object tags, receiver/target object IDs, and typed argument fields. `ignoreExtraArgs` preserves mixed-version compatibility for older operation arities.

Control flow: `parse` initializes the object table with `db1` and `db2`, scans operations until EOF, then calls `computeDerivedFields`. `parseOp` recognizes `Init(args)`, `obj.Method(args)`, and `target = obj.Method(args)`. `makeOp` validates method existence, receiver tag compatibility, assignment requirements, and argument syntax before constructing the concrete `op`. `parseArgs` handles fixed args plus supported variadic/list args: iterator flags, object IDs, key ranges, checkpoint/download spans, and external objects with bounds.

State and persistence: the parser maintains only in-memory object-definition state and derived relationship maps. It does not persist data, but parsed operations drive later DB, batch, iterator, snapshot, and external-object state.

Dependencies and integration: depends on Pebble operation types in the metamorphic package, `pebble.KeyRange`, `CheckpointSpan`, `DownloadSpan`, `blockiter.SyntheticPrefix/Suffix`, and `parseObjID` from `utils.go`. It integrates tightly with `formatOps`, operation `rewriteKeys`, and concurrent execution through derived fields.

Risks and edge cases: panics are converted to parse errors only at the top level, so helper assertions must be carefully contextualized. Synthetic-prefix validation assumes bounds share the prefix. `parseList` only accepts strings, identifiers, and integers. Derived-field computation silently depends on earlier object-creation operations; malformed but syntactically valid orderings may leave zero derived IDs.

Test signals: `parser_test.go` covers datadriven parsing, 10k-operation random round trips, multi-instance operation streams, and preservation of nil iterator bounds.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/parser.go -->
