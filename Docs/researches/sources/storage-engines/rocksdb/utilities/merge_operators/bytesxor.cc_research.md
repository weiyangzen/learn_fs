# sources/storage-engines/rocksdb/utilities/merge_operators/bytesxor.cc

## Purpose
This file implements `BytesXOROperator`, an associative merge operator that XORs byte arrays.

## Important APIs, types, and functions
`MergeOperators::CreateBytesXOROperator()` returns a shared `BytesXOROperator`.

`BytesXOROperator::Merge()` ignores key/logger, delegates to `XOR()`, and returns true.

`XOR()` copies the operand when no existing value exists. Otherwise it XORs bytes up to the shorter length and appends the remaining tail from the longer input unchanged.

## Control flow
The merge path clears and reserves `new_value`, processes the common prefix byte-by-byte, then copies the suffix from whichever input is longer.

## State and persistence behavior
The operator is stateless. Persistent DB value state is determined solely by merge operands and compaction/get merge evaluation.

## Dependencies and integration points
It depends on `bytesxor.h`, standard algorithms/strings, and the RocksDB associative merge interface. It is registered by `merge_operators.cc` under class name `"BytesXOR"` and nickname `"bytesxor"`.

## Risks and edge cases
The operator is described as XORing same-sized byte arrays but accepts different sizes by carrying the longer suffix unchanged. XOR on signed `char` operands is stored back into `char`, which is byte-preserving but may be surprising in textual contexts. It always reports success and does not validate input sizes.

## Test signals
No direct test is listed in this subset. Expected coverage is through merge operator unit tests or factory tests elsewhere.
