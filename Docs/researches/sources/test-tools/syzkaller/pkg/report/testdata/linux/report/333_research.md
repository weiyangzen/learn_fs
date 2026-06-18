<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/333 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/333

## Purpose
This fixture exercises corrupted-stack-end parsing when the visible interrupted RIP is a lockdep helper, not the final writeback worker. It ensures syzkaller still reports `wb_workfn`.

## Important APIs, Types, And Functions
The raw stack starts at `lock_is_held_type`, then moves through `rcu_read_lock_held`, slab shrinkers, ext4 inode/extent write paths, and finally `wb_workfn`. The expected API contract sets title, alt, type `DoS`, and panicked state.

## Control Flow
The parser must use panic context and workqueue/stack ranking rather than the first RIP alone. It trims a long but coherent writeback/reclaim trace and assigns the stable stack-overflow alt title.

## State And Persistence
Persistent metadata is the parser oracle. Runtime state in the log includes writeback worker identity, ext4 allocation state, and panic status.

## Dependencies And Integration Points
It depends on report frame scoring, lockdep helper filtering, ext4 stack recognition, and panic handling in `pkg/report`.

## Risks
A naive first-frame title would become `lock_is_held_type`, which would hide the intended stack-overflow signature.

## Test Signals
The parsed title must remain `kernel panic: corrupted stack end in wb_workfn`, with type `DoS` and panicked flag.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/333 -->
