<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/271 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/271

## Purpose
This fixture covers RCU stall parsing in FUSE device release. The expected title is `INFO: rcu detected stall in fuse_dev_release`, alt `stall in fuse_dev_release`, and type `HANG`.

## Important APIs, Types, and Functions
Headers include `TITLE`, `ALT`, and `TYPE`. Parser paths include RCU stall detection, task stack extraction, and later grace-period kthread diagnostics. Key symbols include `sched_show_task`, `print_other_cpu_stall`, `check_cpu_stall`, `rcu_check_callbacks`, `native_queued_spin_lock_slowpath`, `request_end`, `end_requests`, `fuse_dev_release`, `__fput`, `task_work_run`, `exit_to_usermode_loop`, and `rcu_gp_kthread`.

## Control Flow
The reporter sees a detected-stalls report, follows the stalled task stack through request completion into `fuse_dev_release`, then sees additional RCU kthread starvation output. The title must come from the stalled task, not the diagnostic kthread.

## State and Persistence Behavior
The file persists expected HANG metadata and a 59-line raw log. It owns no runtime state.

## Dependencies and Integration Points
It depends on RCU stall parser support for both task and kthread diagnostic sections, and on hang title generation.

## Risks and Edge Cases
The log has two RCU-related stack sections. Choosing the later `rcu_gp_kthread` stack would hide the FUSE regression.

## Test Signals
Expected parse is the FUSE release RCU-stall title and alt with type `HANG`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/271 -->
