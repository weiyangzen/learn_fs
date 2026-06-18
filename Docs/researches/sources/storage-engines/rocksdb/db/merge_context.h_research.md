# sources/storage-engines/rocksdb/db/merge_context.h

## Purpose
`merge_context.h` defines `MergeContext`, the small operand accumulator used while resolving RocksDB merge operations in memtables, version reads, and compaction. It preserves merge operands, copies unpinned slices, and can expose operands in either merge order or reverse traversal order.

## Important APIs, types, and functions
`empty_operand_list` is a shared empty vector returned when no operands have been initialized. `MergeContext` exposes a public `GetMergeOperandsOptions* get_merge_operands_options` used by raw merge-operand reads to control continuation.

`Clear` removes stored operands and copied storage without releasing the lazily allocated vectors. `PushOperand` appends a newly encountered operand while setting backward direction, which corresponds to newest-first traversal. `PushOperandBack` appends while setting forward direction. Both accept an `operand_pinned` flag; pinned operands are referenced directly, while unpinned operands are copied into owned `std::string`s.

`GetNumOperands`, `GetOperand`, `GetOperands`, `GetOperandsDirectionForward`, and `GetOperandsDirectionBackward` expose the accumulated operands. The direction accessors mutate internal ordering if needed by reversing `operand_list_`.

Private helpers `Initialize`, `SetDirectionForward`, and `SetDirectionBackward` lazily allocate storage and maintain the `operands_reversed_` flag.

## Control flow
Point lookups and compactions encounter records newest-to-oldest. They call `PushOperand` as merge operands are found, which leaves the logical order reversed/newest-first. When a full merge is attempted, callers use `GetOperands` or `GetOperandsDirectionForward`, causing a reverse if necessary so operands are passed to the merge operator in the documented merge order. When `MergeOperator::ShouldMerge` needs backward ordering, callers use `GetOperandsDirectionBackward`.

If a memtable value is being returned as a raw merge operand with `do_merge=false`, unmerged values can also be pushed into the context. The context copies any operand not pinned by the iterator/memtable so returned slices remain valid until the next mutation or clear.

## State and persistence behavior
`MergeContext` is purely in-memory and per-operation. Its owned strings provide temporary persistence for unpinned slices during a lookup or compaction step. Returned references are explicitly invalidated by subsequent calls that can reverse, clear, or append operands.

## Dependencies and integration points
The type integrates with `rocksdb/db.h` for `GetMergeOperandsOptions`, `rocksdb/slice.h`, memtable `Get`, `MemTableListVersion::GetMergeOperands`, `MergeHelper`, DB point reads, and compaction. It is a key ordering bridge between internal iterators that scan backward by sequence number and user merge operators that expect operands in application order.

## Risks and edge cases
The direction-changing accessors are `const` but mutate internal order. Callers must not hold references across later context calls unless they copy. Pinned operands require the underlying storage to remain valid for the context lifetime. Repeated direction flips reverse the vector in place and can be surprising in debugger traces. The public options pointer is not owned and must outlive the operation.

## Test signals
Merge ordering is indirectly validated by `memtable_list_test.cc`, `merge_helper_test.cc`, and `merge_test.cc`. Important signals are correct string append ordering across memtables, partial-merge output order, raw merge operand reads, and continuation callback behavior in memtable lookup paths.
