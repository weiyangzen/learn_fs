<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/207 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/207

## Purpose
This fixture verifies hang/stall parsing for an RCU scheduler stall in deferred BPF map freeing. Expected title is `INFO: rcu detected stall in bpf_map_free_deferred`, alt `stall in bpf_map_free_deferred`, and type `HANG`.

## Important APIs, Types, And Functions
The fixture contains an RCU stall report rather than an oops. Parser behavior under test includes `INFO: rcu_sched detected stalls on CPUs/tasks` matching, workqueue context extraction, and hang type mapping. Important frames include `_sched_show_task`, `sched_show_task`, `rcu_check_callbacks`, `update_process_times`, `tick_sched_timer`, `hrtimer_interrupt`, `free_percpu`, `array_map_free`, `bpf_map_free_deferred`, `process_one_work`, `worker_thread`, `kthread`, and `ret_from_fork`.

## Control Flow
The reporter detects the RCU stall line, parses the shown running task `kworker/0:0`, and uses the workqueue function `bpf_map_free_deferred` for the title. Runtime flow is workqueue execution of BPF map cleanup stuck or slow enough to trigger RCU stall reporting.

## State And Persistence
Persistent state is the expected metadata and a 45-line stall report. Dynamic state includes jiffies, CPU ids, task state, addresses, and RCU grace-period counters.

## Dependencies And Integration Points
It depends on Linux hang/RCU-stall parsing, workqueue function extraction, and alternate-title generation for stalls. It integrates with syzkaller's report parser tests for non-panic hangs.

## Risks
The parser could fail to parse a report without `BUG:` or `WARNING:` prefixes, or title from timer interrupt frames instead of `bpf_map_free_deferred`. It must also classify as `HANG`, not `WARNING`.

## Test Signals
Assert exact title, alt, and type `HANG`. The report should include the workqueue line `Workqueue: events bpf_map_free_deferred`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/207 -->
