<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/249 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/249

## Purpose
This fixture checks warning parsing for a sleep-in-invalid-state report reached through `rfkill_fop_read`. The expected title is `WARNING in rfkill_fop_read`, type `WARNING`, and `PANICKED: Y`.

## Important APIs, Types, and Functions
Headers include `TITLE`, `TYPE`, and `PANICKED`. Parser components include generic WARNING extraction, frame selection, panic-on-warn detection, and crash type mapping. The kernel stack includes `__might_sleep`, `prepare_to_wait_event`, `panic`, `warn_slowpath_common`, `warn_slowpath_fmt`, `mutex_lock_nested`, `rfkill_fop_read`, `do_loop_readv_writev`, `do_readv_writev`, `vfs_readv`, and `SyS_readv`.

## Control Flow
The Linux reporter starts at `WARNING: CPU... __might_sleep`, observes the explanatory line about blocking ops when not `TASK_RUNNING`, then traverses the call trace. Although panic frames appear early because `panic_on_warn` is set, the report title must use the non-helper frame `rfkill_fop_read`.

## State and Persistence Behavior
The checked-in state is a compact raw kernel warning plus expected metadata. There is no executable state, persistence, or mutation beyond the fixture file.

## Dependencies and Integration Points
This depends on warning-pattern extraction, skip lists for generic warn/panic helpers, and panic line recognition. It integrates through `Reporter.Parse` and `ParseTest.Equal`.

## Risks and Edge Cases
Panic-on-warn stack frames can obscure the original warning site. The parser must also avoid choosing scheduler helper frames such as `__might_sleep` when a better subsystem frame exists.

## Test Signals
Stable signals are title `WARNING in rfkill_fop_read`, type `WARNING`, and panic flag set.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/249 -->
