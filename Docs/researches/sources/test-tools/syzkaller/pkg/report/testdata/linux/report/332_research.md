<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/332 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/332

## Purpose
This fixture covers the same corrupted-stack-end panic class on a 4.20-rc7 kernel, with an ext4 path that includes `__remove_mapping` and bitmap loading. It validates version-insensitive title extraction.

## Important APIs, Types, And Functions
Important frames include `panic`, `__schedule`, `_raw_spin_unlock_irqrestore`, `__remove_mapping`, `shrink_page_list`, `ext4_read_block_bitmap_nowait`, `ext4_mb_mark_diskspace_used`, `ext4_writepages`, and `wb_workfn`.

## Control Flow
The parser enters through the panic marker, then finds the writeback context and expected title. The body has normal call-trace structure without a separate explicit `REPORT:` block.

## State And Persistence
Expected persisted state is `TYPE: DoS`, `ALT: stack-overflow in wb_workfn`, and `PANICKED: Y`. The raw log preserves version, register, and ext4 allocator details for regression coverage.

## Dependencies And Integration Points
This depends on Linux stack-overflow title normalization and syzkaller's logic that avoids choosing allocator or filesystem helper frames over the worker function.

## Risks
The report might be misclassified as a generic panic if the `corrupted stack end detected inside scheduler` string is not recognized.

## Test Signals
Parser output must match the shared `wb_workfn` title and alt and preserve the panicked flag.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/332 -->
