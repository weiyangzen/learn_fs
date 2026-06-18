<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/350 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/350

## Purpose
This large fixture verifies soft-lockup parsing with an explicit expected `REPORT:` block. The expected title is `BUG: soft lockup in smp_call_function`, with alternatives for `smp_call_function_many` and generic stall wording, type `HANG`, panicked.

## Important APIs, Types, And Functions
The root marker is `watchdog: BUG: soft lockup - CPU#2 stuck for 136s`. The primary stack includes `smp_call_function_many`, `smp_call_function`, `on_each_cpu`, `text_poke_bp`, jump-label updates, perf tracepoint teardown, `perf_event_release_kernel`, and syscall exit. NMI backtraces for other CPUs include `process_srcu`, DRM/vkms timer paths, and execve fault handling.

## Control Flow
The parser selects the watchdog soft lockup as the root, generates several alternative titles, then the test compares the parser-selected body against the explicit `REPORT:` block. Panic state is detected from `Kernel panic - not syncing: softlockup: hung tasks`.

## State And Persistence
Persistent state includes title, three alt titles, type `HANG`, panicked flag, raw log, and explicit expected report. Runtime state includes stuck CPU, NMI backtraces, ftrace buffer content, and perf/vkms subsystem activity.

## Dependencies And Integration Points
It depends on soft-lockup recognizers, NMI backtrace inclusion, `REPORT:` handling in `report_test.go`, alt title generation for stalls, and hang classification.

## Risks
Report-boundary changes are high risk because this fixture asserts a large explicit report body. Frame scoring can also choose `smp_call_function_many`, which is allowed only as an alternative.

## Test Signals
Stable parsing keeps primary title `BUG: soft lockup in smp_call_function`, all listed alternatives, type `HANG`, panicked, and a report body beginning with the watchdog soft-lockup line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/350 -->
