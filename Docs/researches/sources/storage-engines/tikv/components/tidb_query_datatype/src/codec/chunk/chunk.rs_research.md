# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/chunk/chunk.rs

## Purpose
Implements `Chunk`, a compact columnar row container compatible with TiDB chunk encoding. It supports appending datums, iterating rows, and encoding/decoding chunks for tests.

## APIs, Flow, And State
`Chunk` owns `Vec<Column>`. `new` builds one `Column` per `FieldType`; `reset` clears reusable buffers; `num_cols`, `num_rows`, `append_datum`, `get_row`, and `iter` expose row/column operations. `decode_for_test` reconstructs columns from encoded bytes. `ChunkEncoder::write_chunk` serializes each column. `Row` is a lightweight `(chunk, index)` view with `get_datum`, and `RowIterator` walks row indexes until `num_rows`.

## Dependencies And Integration
Depends on `Column`, `ChunkColumnEncoder`, `FieldTypeAccessor`, `Datum`, and codec buffer writer traits. It integrates with lazy batch chunk encoding and TiDB coprocessor response formats.

## Risks And Test Signals
`num_rows` trusts the first column length, so callers must keep columns aligned. `append_datum` indexes columns directly and can panic on bad indexes. Tests cover appending multiple datum types, constructing chunks from lazy raw columns, chunk encode/decode round trips, and benches for raw-datum to chunk encoding.
