<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/194 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/194

## Purpose
This fixture validates lockdep title selection for perf event release. Expected title is `possible deadlock in perf_event_release_kernel`, type `LOCKDEP`.

## Important APIs, Types, And Functions
The static report uses lockdep warning text with important frames `perf_trace_destroy`, `perf_event_release_kernel`, `perf_event_for_each_child`, `perf_ioctl`, `do_vfs_ioctl`, `SyS_ioctl`, `entry_SYSCALL_64_fastpath`, `perf_event_init_cpu`, `perf_event_init`, `start_kernel`, `x86_64_start_reservations`, `x86_64_start_kernel`, `secondary_startup_64`, `cpuhp_invoke_callback`, `_cpu_up`, and `do_cpu_up`.

## Control Flow
The Linux reporter parses the circular dependency and should select the semantic release function rather than `perf_trace_destroy` or ioctl wrappers. Runtime flow is user ioctl-driven perf event teardown interacting with perf initialization/hotplug dependency paths.

## State And Persistence
The fixture persists 257 lines of lockdep report and expected metadata. Task ids, lock addresses, and CPU hotplug details are volatile.

## Dependencies And Integration Points
It integrates with syzkaller's Linux lockdep parser and perf-event title heuristics. It complements reports 191-193 by covering release/teardown rather than read/init.

## Risks
The parser could select `perf_trace_destroy`, `perf_ioctl`, or `perf_event_for_each_child` instead of `perf_event_release_kernel`. Another risk is losing syscall context if report truncation happens too early.

## Test Signals
Check exact title and `LOCKDEP` type. The report should preserve the perf release stack, ioctl syscall path, and perf initialization dependency side.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/194 -->
