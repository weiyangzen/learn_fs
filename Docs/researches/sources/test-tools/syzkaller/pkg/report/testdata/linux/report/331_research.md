<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/331 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/331

## Purpose
This is a second `corrupted stack end` writeback fixture for the same expected crash title as report 330. It protects parser stability across a shorter path through allocator sleep instead of interrupt preemption.

## Important APIs, Types, And Functions
Key markers are the panic line, workqueue `writeback wb_workfn`, and stack frames `schedule_timeout_uninterruptible`, `__alloc_pages_slowpath`, `ext4_mb_load_buddy_gfp`, `ext4_writepages`, `wb_writeback`, and `wb_workfn`.

## Control Flow
After headers, the parser scans the panic body, builds the report around the panic, and derives `wb_workfn` from the workqueue/writeback stack. It must normalize this variant to the same title and alternative as neighboring stack-end fixtures.

## State And Persistence
The file persists expected `DoS` and `PANICKED` state. It has no mutable state; PIDs, timestamps, and allocation state in the log are raw kernel context.

## Dependencies And Integration Points
It integrates with the Linux panic parser, scheduler stack-overflow recognizer, workqueue frame selection, and ext4/writeback symbol filtering.

## Risks
The immediate frames are scheduler and page allocator functions, so frame-priority changes can regress attribution away from `wb_workfn`.

## Test Signals
The report should parse to `kernel panic: corrupted stack end in wb_workfn` with `stack-overflow in wb_workfn` and `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/331 -->
