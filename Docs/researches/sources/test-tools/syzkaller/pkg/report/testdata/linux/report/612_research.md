# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/612

## Purpose
This fixture validates an RCU stall hang attributed to `ext4_file_read_iter`. The expected alternate title is `stall in ext4_file_read_iter`.

## Important APIs, types, and functions
The log contains RCU/timer frames and multiple trace fragments, including `lock_acquire`, `copy_user_generic_string`, `preempt_schedule_irq`, `exit_to_user_mode_prepare`, and ext4 read-path attribution through `ext4_file_read_iter`.

## Control flow
The report is assembled from an RCU stall and repeated CPU backtrace sections. The parser must skip generic interrupt, lockdep, unwind, and user-copy frames to keep the filesystem read iterator as the useful site.

## State and persistence behavior
The fixture stores expected metadata and a noisy raw log. No state is updated by the file itself.

## Dependencies and integration points
It integrates RCU hang recognition with ext4/VFS stack parsing and frame-priority heuristics.

## Risks and test signals
The risk is unstable title selection from repeated stacks. The stable signal is `TYPE: HANG` with title `INFO: rcu detected stall in ext4_file_read_iter`.
