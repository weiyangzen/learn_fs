# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/chunked_vec_enum.rs

## Purpose
Stores `Option<Enum>` values by splitting enum numeric values from display names while preserving borrowed `EnumRef` access.

## Important APIs, Types, And Functions
`ChunkedVecEnum` contains `values: ChunkedVecSized<Int>` and `names: ChunkedVecBytes`. Public accessors are `get`, `as_vec_int`, and `as_vec_bytes`. It implements `ChunkedVec<Enum>`, `PartialEq`, `ChunkRef<EnumRef>`, `From<Vec<Option<Enum>>>`, and `UnsafeRefInto`.

## Control Flow
`push_data` writes the enum's 1-based value as `i64` and the name bytes. `push_null` writes null to both child vectors. `get` reads the numeric reference and name, then constructs `EnumRef` using `retain_lifetime_transmute` for matching lifetimes. `append`, `truncate`, and `to_vec` delegate to both children in lockstep.

## State And Persistence
In-memory owned child vectors. Both child vectors duplicate null bitmaps; this is explicitly accepted to satisfy borrowing/lifetime constraints.

## Dependencies And Integration Points
Composes `ChunkedVecSized<Int>` and `ChunkedVecBytes`, integrates with evaluator `ChunkRef`, and exposes child vectors for consumers that need numeric or byte representations.

## Risks
The two child vectors must remain length/null aligned; any future direct mutation can corrupt representation. Unsafe lifetime retention is sound only while the chunk owns both children. Duplicated bitmaps waste memory.

## Test Signals
Local tests cover basics, truncation, append/drain behavior, and borrowed `EnumRef` equality.
