<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/330 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/330

## Purpose
This fixture verifies parsing of a scheduler-detected stack overflow during ext4 writeback. The expected title is `kernel panic: corrupted stack end in wb_workfn`, with alt `stack-overflow in wb_workfn`, type `DoS`, and `PANICKED: Y`.

## Important APIs, Types, And Functions
The important kernel path is `Kernel panic - not syncing: corrupted stack end detected inside scheduler`, workqueue `writeback wb_workfn`, and a stack from `__schedule` through memory reclaim and ext4 allocation/writeback: `shrink_page_list`, `ext4_mb_new_blocks`, `ext4_ext_map_blocks`, `ext4_writepages`, and `wb_workfn`.

## Control Flow
The Linux reporter must treat the panic line as the root oops, then walk the stack to the best frame for title attribution. The selected function is not the immediate scheduler frame, but the writeback worker context visible in the workqueue and lower stack.

## State And Persistence
Persistent state is the expected metadata and raw panic log. The log includes stack-depth warnings from other processes, which are transient state used to test that unrelated depth messages do not become the title.

## Dependencies And Integration Points
This depends on panic-line parsing, stack-overflow alternative title generation, workqueue context recognition, and crash type mapping to `DoS`.

## Risks
Parser ranking can accidentally choose `__schedule`, `retint_kernel`, or memory reclaim frames instead of `wb_workfn`.

## Test Signals
Stable output should keep the `wb_workfn` title and alt, mark the report panicked, and ignore unrelated `used greatest stack depth` lines as secondary noise.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/330 -->
