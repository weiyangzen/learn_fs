# sources/storage-engines/rocksdb/utilities/agg_merge/agg_merge.cc

## Purpose

This file implements RocksDB's experimental aggregation merge operator. It lets values and merge operands carry an aggregation function name plus a payload, then applies registered `Aggregator` plugins during full or partial merge. When aggregation cannot proceed, it preserves the original operands in an encoded error value rather than failing the DB operation.

## Important APIs, types, and functions

Global API implementations are `AddAggregator`, `EncodeAggFuncAndPayload`, `ExtractAggFuncAndValue`, `ExtractList`, and `GetAggMergeOperator`. Internal symbols include the process-global `func_map`, reserved names `kUnnamedFuncName` and `kErrorFuncName`, `EncodeAggFuncAndPayloadNoCheck`, `AggMergeOperator::Accumulator`, `PackAllMergeOperands`, `FullMergeV2`, and `PartialMergeMulti`.

## Control flow

`EncodeAggFuncAndPayload` validates the function name and writes a length-prefixed function slice followed by raw payload. `Accumulator::Add` decodes each operand, selects the first non-empty function, optionally rejects partial aggregation when the registered aggregator opts out, and handles function switches by fully aggregating older values before adding the next function's payload. `FullMergeV2` feeds the existing value and operands through the accumulator, emits the aggregate on success, or packs all inputs under `kErrorFuncName` on failure. `PartialMergeMulti` only returns true if all operands can be safely partially aggregated.

## State and persistence behavior

Registered aggregators live in a static unordered map and are shared by all operator instances. The merge operator singleton is held by `STATIC_AVOID_DESTRUCTION`. Per-merge scratch state is a thread-local accumulator to avoid repeated allocation while remaining safe for concurrent merge invocations. Persisted DB values use length-prefixed function names plus aggregator-defined payload bytes; error values use `kErrorFuncName` plus a length-prefixed list of original encoded operands.

## Dependencies and integration points

The implementation plugs into RocksDB's `MergeOperator` interface and uses `Slice`, `Status`, `PutLengthPrefixedSlice`, `GetLengthPrefixedSlice`, and `port/lang.h`. Public declarations come from `include/rocksdb/utilities/agg_merge.h`, while internal class declarations live in `agg_merge_impl.h`. Applications install it through `Options::merge_operator = GetAggMergeOperator()` and register functions with `AddAggregator`.

## Risks

`func_map` mutation is not synchronized and the public header says aggregators should be registered before use. Duplicate registrations are silently ignored by `emplace` but still return OK, which can surprise users. Stored encodings are explicitly experimental and subject to change. Function switches require payload format compatibility across aggregators. Partial merge is intentionally conservative, but a buggy `DoPartialAggregate` implementation can produce semantically wrong intermediate values.

## Test signals

`agg_merge_test.cc` exercises sum, multiplication, last-three list aggregation, Put-with-unnamed-function behavior, function switching across flush and compaction, unregistered functions, invalid payloads, and error-list extraction.
