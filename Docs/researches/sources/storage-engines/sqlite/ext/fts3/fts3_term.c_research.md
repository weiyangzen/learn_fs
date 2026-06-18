# sources/storage-engines/sqlite/ext/fts3/fts3_term.c

## Purpose

Defines the test-only `fts4term` virtual table module, which exposes raw full-text index terms and their docid/column/position occurrences. It is not production FTS code and is compiled under `SQLITE_TEST`.

## Important APIs, types, and functions

`Fts3termTable` stores a synthetic `Fts3Table` and index number. `Fts3termCursor` embeds `Fts3MultiSegReader`, `Fts3SegFilter`, EOF state, doclist pointer, rowid, docid, column, and position. Virtual-table callbacks are `fts3termConnectMethod()`, `fts3termDisconnectMethod()`, `fts3termBestIndexMethod()`, `fts3termOpenMethod()`, `fts3termCloseMethod()`, `fts3termFilterMethod()`, `fts3termNextMethod()`, `fts3termEofMethod()`, `fts3termColumnMethod()`, and `fts3termRowidMethod()`. `sqlite3Fts3InitTerm()` registers the module as `fts4term`.

## Control flow

Connect expects the target FTS table name and optional index number, declares schema `term, docid, col, pos`, and builds enough `Fts3Table` metadata to read segment tables. Filtering initializes a full segment scan requiring positions. `fts3termNextMethod()` steps segment readers term by term and decodes the current doclist: docid deltas, column markers, and position deltas are translated to output columns.

## State and persistence

The module owns no persistent table. It reads existing FTS segment state through the synthetic table object and maintains cursor-local decoded position state. Disconnect finalizes prepared statements and frees synthetic metadata.

## Dependencies and integration points

Depends on segment-reader APIs such as `sqlite3Fts3SegReaderCursor()`, `sqlite3Fts3SegReaderStart()`, `sqlite3Fts3SegReaderStep()`, `sqlite3Fts3SegReaderFinish()`, `sqlite3Fts3SegmentsClose()`, and FTS varint decoding. It integrates with the SQLite virtual-table API and the Tcl/SQLite test suite.

## Risks and test signals

Risks include malformed doclists, incorrect synthetic `Fts3Table` fields, index-number mismatches for prefix indexes, and exposing implementation ordering assumptions. Test signals are ordered `term, docid, col, pos` scans, prefix-index constructor arguments, segment-reader cleanup, and corrupt-index behavior under debug tests.
