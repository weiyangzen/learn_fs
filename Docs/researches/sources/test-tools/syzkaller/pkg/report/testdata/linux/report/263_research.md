<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/263 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/263

## Purpose
This fixture verifies RCU stall parsing for ALSA sequencer writes. The expected title is `INFO: rcu detected stall in snd_seq_write`, alt `stall in snd_seq_write`, and type `HANG`.

## Important APIs, Types, and Functions
Headers include `TITLE`, `ALT`, and `TYPE`. Parser paths include RCU stall detection, NMI backtrace parsing, hang-title normalization, and frame selection. Key symbols include `dump_stack`, `nmi_cpu_backtrace`, `rcu_dump_cpu_stacks`, `print_cpu_stall`, `rcu_check_callbacks`, `lock_release`, `__might_fault`, `_copy_from_user`, `snd_seq_write`, `__vfs_write`, `vfs_write`, and `__x64_sys_write`.

## Control Flow
The reporter sees a self-detected `rcu_sched` CPU stall, NMI backtrace, interrupt frames, then the stalled task stack. It must title the hang at `snd_seq_write`, not at RCU timer or interrupt helper frames.

## State and Persistence Behavior
The fixture has no mutable state. Expected persistent metadata is title, alt title, and `HANG` type over an 85-line raw log.

## Dependencies and Integration Points
It depends on Linux RCU stall regexes, stack parsing across IRQ boundaries, and hang crash-type mapping.

## Risks and Edge Cases
The first stack section belongs to RCU/NMI machinery; the parser must find the task frame after interrupt unwinding. User copy and write helpers are nearby lower-value frames.

## Test Signals
Stable output is `INFO: rcu detected stall in snd_seq_write`, alt `stall in snd_seq_write`, and type `HANG`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/263 -->
