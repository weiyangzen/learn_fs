# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/chunk/column.rs

## Purpose
Implements the low-level columnar storage unit used by `Chunk`. `Column` stores null metadata, fixed or variable width payload data, and type-specific encode/decode routines for TiDB datum and chunk formats.

## APIs, Flow, And State
`Column` state includes `length`, `null_cnt`, `null_bitmap`, `var_offsets`, `data`, and `fixed_len`. `new` maps field types to fixed widths or variable layout. `from_raw_datums` decodes selected raw datum rows based on `EvalType`; `from_vector_value` converts typed vectors to chunk columns. `get_datum` reconstructs `Datum` values by field type. Append APIs cover nulls, signed/unsigned ints, bit, float/double, bytes, time, duration, decimal, JSON, vector-float32, and enum. Variable columns maintain a leading zero offset and append one offset per row; fixed columns resize data after writes. `ChunkColumnEncoder::write_chunk_column` writes length, null count, optional bitmap, optional offsets, and payload bytes.

## Dependencies And Integration
Depends on TiKV codec buffer traits, number codecs, MySQL datatype encoders/decoders, `VectorValue`, `EvalContext`, `FieldTypeAccessor`, `FieldTypeFlag`, and datum flags. It is the conversion point between row datum encoding, vectorized evaluation values, and chunk response bytes.

## Risks And Test Signals
Risks concentrate in datum flag handling, unsigned casts, bit field length handling, unimplemented Set and over-64-bit Bit paths, null bitmap correctness, and var-offset consistency. Tests cover each scalar family, chunk round trips, and raw/lazy conversion paths.
