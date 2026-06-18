# Research: sources/storage-engines/rocksdb/include/rocksdb/utilities/agg_merge.h

- **Purpose:** Declares an experimental aggregation merge-operator utility that multiplexes merge operands to registered aggregation functions by function name.
- **Important APIs/types/functions:** `Aggregator::Aggregate()` combines values in reverse insertion order and `DoPartialAggregate()` controls partial aggregation. `AddAggregator()` registers a named plugin. `GetAggMergeOperator()` returns the singleton merge operator. `EncodeAggFuncAndPayload()`, `ExtractAggFuncAndValue()`, and `ExtractList()` encode/decode operands and error lists. `kUnnamedFuncName` and `kErrorFuncName` are reserved function names.
- **Control flow:** Users register aggregators, install the singleton merge operator, encode Put/Merge payloads with function names, and Reads trigger aggregation. Changing function names for a key causes prior operands to be aggregated and used as the first payload for the new function.
- **State and persistence:** Encoded function/payload data is stored as DB values and merge operands. Aggregator registry is process-global and not thread-safe to mutate concurrently with merge operation use.
- **Dependencies:** Depends on `MergeOperator`, `Slice`, `Status`, strings, and vectors.
- **Integration points:** Bridges RocksDB merge semantics to reusable aggregation functions, including functions inspired by SQL engines or third-party aggregation libraries.
- **Risks:** Encoding format is explicitly subject to change. Missing aggregators or aggregation errors encode an error function with operand lists rather than necessarily failing the DB operation. Registry mutation races can affect active DBs.
- **Test signals:** Tests should cover encoding/decoding, unnamed-to-named transitions, function switching, partial aggregation, missing/error aggregators, singleton reuse, and registry initialization before DB open.
