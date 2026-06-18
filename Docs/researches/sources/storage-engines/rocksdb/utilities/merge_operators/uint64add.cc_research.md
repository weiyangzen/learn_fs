# sources/storage-engines/rocksdb/utilities/merge_operators/uint64add.cc

## Purpose
This file implements `UInt64AddOperator`, an associative merge operator that treats operands and existing values as fixed-width little-endian uint64 values and stores their sum.

## Important APIs, types, and functions
`UInt64AddOperator::Merge()` decodes existing value if present, decodes the operand, clears `new_value`, writes `orig_value + operand` with `PutFixed64()`, and returns true.

`DecodeInteger()` returns `DecodeFixed64()` when the slice is exactly 8 bytes. Otherwise it logs a corruption message when a logger is available and returns zero.

`MergeOperators::CreateUInt64AddOperator()` returns a shared `UInt64AddOperator`.

## Control flow
The merge path is constant-time: decode existing, decode operand, add, encode. Corrupt-sized inputs are tolerated as zero rather than failing the merge.

## State and persistence behavior
The operator is stateless. Persistent DB values are fixed64-encoded sums. Overflow wraps according to unsigned 64-bit arithmetic.

## Dependencies and integration points
It depends on RocksDB logging, env/merge/slice APIs, `util/coding.h`, and merge factories. It is registered under `"UInt64AddOperator"` and `"uint64add"`.

## Risks and edge cases
Malformed values silently become zero except for optional logging. Overflow is not checked. Endianness/encoding must match `PutFixed64` and `DecodeFixed64`; callers storing decimal strings will get corruption-as-zero semantics.

## Test signals
No direct test in this subset. Expected coverage is through merge operator unit tests elsewhere.
