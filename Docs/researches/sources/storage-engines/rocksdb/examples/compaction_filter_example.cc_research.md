# sources/storage-engines/rocksdb/examples/compaction_filter_example.cc

## Purpose
`compaction_filter_example.cc` demonstrates compaction filtering of merge operands. It shows how a `CompactionFilter` can remove selected operands before a custom `MergeOperator` performs full merge.

## Important APIs and control flow
`MyMerge` implements `MergeOperator::FullMergeV2()`, copies an existing value if present, iterates operands, asserts no operand equals `"bad"`, and assigns the latest operand as the merged value. `MyFilter` implements `CompactionFilter::Filter()` for regular values and `FilterMergeOperand()` for merge operands. It increments counters and returns true for merge operands whose existing value is `"bad"`.

`main()` removes the temp DB directory with a platform-specific shell command, opens a DB with `options.merge_operator` and `options.compaction_filter`, writes several merge operands including `"bad"`, runs full `CompactRange()`, and asserts that regular-value filter count is zero while merge-operand filter count is six.

## State, persistence, and integration
The example persists a DB under `/tmp/rocksmergetest` or Windows temp. It integrates with RocksDB compaction filters, merge operators, merge writes, and manual compaction. Filter state is mutable counters on a stack-owned filter referenced by `Options`.

## Risks and test signals
Using `system("rm -rf ...")` or `rmdir` with string concatenation is acceptable for fixed example paths but unsafe as a general pattern. The filter pointer is non-owning, so the filter must outlive the DB. The example does not close/destroy through RAII beyond `unique_ptr<DB>`. Test signals are `CompactRange()` success, six merge operand filter invocations, zero regular value filter invocations, and no assertion in the merge operator seeing `"bad"`.
