<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/190 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/190

## Purpose
This fixture is the write-side VCS counterpart to report 189. Expected title is `possible deadlock in vcs_write`, type `LOCKDEP`, covering circular locking in console virtual terminal writes plus pipe splice.

## Important APIs, Types, And Functions
The static report exercises lockdep parsing with key frames `vcs_write`, `pipe_lock`, `lock_acquire`, `__mutex_lock`, `mutex_lock_nested`, `iter_file_splice_write`, `SyS_splice`, `put_ucounts`, `wait_for_completion`, `devtmpfs_create_node`, `device_add`, `device_create_groups_vargs`, `device_create`, `vcs_make_sysfs`, `vc_allocate`, `con_install`, and `tty_init_dev`.

## Control Flow
The Linux reporter parses the circular-locking warning and should use the active write path `vcs_write` for the title. The runtime trace indicates splice/write interaction with VCS and a dependency chain through console/TTY setup and device creation.

## State And Persistence
The 163-line log and expected metadata are persistent fixture state. Runtime lock addresses, task ids, console numbers, and stack addresses are volatile.

## Dependencies And Integration Points
It integrates with the lockdep parser and with VFS/TTY stack title heuristics. It complements report 189 to ensure read and write VCS paths remain distinct.

## Risks
Title selection can drift to `pipe_lock`, `vcs_make_sysfs`, or the devtmpfs side. Another risk is deduplicating the write case with the read case and losing coverage.

## Test Signals
Assert exact title `possible deadlock in vcs_write` and type `LOCKDEP`. The report should include both the `vcs_write` stack and dependency frames around console/TTY device creation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/190 -->
