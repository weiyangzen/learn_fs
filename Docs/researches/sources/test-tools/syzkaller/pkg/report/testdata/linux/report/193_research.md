<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/193 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/193

## Purpose
This fixture covers a perf lockdep warning during CPU hotplug initialization. Expected title is `possible deadlock in perf_event_for_each_child`, type `LOCKDEP`.

## Important APIs, Types, And Functions
The report data exercises lockdep parsing with boot/hotplug stacks. Key frames include `perf_event_for_each_child`, `perf_event_ctx_lock_nested`, `__mutex_lock`, `mutex_lock_nested`, `perf_event_init_cpu`, `perf_event_init`, `start_kernel`, `x86_64_start_reservations`, `x86_64_start_kernel`, `secondary_startup_64`, `cpuhp_invoke_callback`, `_cpu_up`, `do_cpu_up`, `cpu_up`, `smp_init`, `kernel_init_freeable`, `kernel_init`, and `ret_from_fork`.

## Control Flow
The parser identifies a circular-locking warning and selects `perf_event_for_each_child` from the perf-side stack. Runtime flow is kernel initialization and CPU hotplug callbacks invoking perf event setup, contrasting with another lock acquisition path in the dependency report.

## State And Persistence
Persistent state is a 193-line lockdep report and expected metadata. CPU ids, lock class addresses, and boot sequence details are dynamic parser input. The file has no mutable state.

## Dependencies And Integration Points
It depends on lockdep parsing, perf stack frame retention, and syzkaller testdata comparison. It expands coverage to warnings during kernel initialization rather than only user syscalls.

## Risks
Boot/hotplug frames can cause title selection to drift to `perf_event_init_cpu` or `start_kernel`; the fixture asserts the child-iteration frame is the stable culprit. Parser filters that drop initialization frames too aggressively can also lose context.

## Test Signals
Expected signal is title `possible deadlock in perf_event_for_each_child` and type `LOCKDEP`. The selected report should include perf event child iteration and CPU initialization/hotplug frames.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/193 -->
