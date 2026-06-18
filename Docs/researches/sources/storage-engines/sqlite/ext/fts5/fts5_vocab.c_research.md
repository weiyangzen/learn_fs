# sources/storage-engines/sqlite/ext/fts5/fts5_vocab.c

## Purpose
`fts5_vocab.c` implements the read-only `fts5vocab` virtual table module. It exposes an existing FTS5 index as `row`, `col`, or `instance` vocab tables.

## Important APIs, Types, And Functions
`sqlite3Fts5VocabInit()` registers the module. `Fts5VocabTable` stores target database/table names, connection, FTS5 global registry, table type, and recursion guard. `Fts5VocabCursor` stores the target FTS5 table, prepared statement, index iterator, structure reference, term bounds, per-column counters, current rowid, term buffer, and instance position state. Virtual table methods implement connect/create, best-index planning, open/filter/next/eof/column/rowid, and cleanup.

## Control Flow
Connect/create parses arguments, supports a TEMP form naming a separate target database, declares the selected schema, and stores dequoted target names. `xBestIndex` recognizes term equality/range constraints and consumes `ORDER BY term ASC`. `xOpen` obtains the target FTS5 cursor id via `MATCH '*id'`, resolves it to `Fts5Table`, flushes pending content to disk, and allocates cursor counters. `xFilter` opens an FTS5 index scan and primes the first row. `xNext` verifies structure stability, aggregates counts for `row`/`col`, or advances individual positions for `instance`. `xColumn` formats output by table type and detail mode.

## State And Persistence
The virtual table persists only its schema. Cursor state is transient. It reads persistent FTS5 index data after flushing pending content and holds a structure reference to detect changes.

## Dependencies And Integration Points
The module uses FTS5 internals: `Fts5Global`, `Fts5Table`, index iterators, poslist decoders, structure refs, cursor-id lookup, and SQLite virtual table APIs.

## Risks
It is tightly coupled to internal FTS5 iterator formats. Detail modes limit available output. Count logic must detect out-of-range column ids as corruption. Term bounds rely on bytewise FTS5 term order. Recursion protection is necessary when resolving target tables.

## Test Signals
Cover all three vocab types, all FTS5 detail modes, multiple columns, deletes/flushes, term equality/ranges, ORDER BY, planner pushdown, and corruption cases with invalid column ids or structure changes.
