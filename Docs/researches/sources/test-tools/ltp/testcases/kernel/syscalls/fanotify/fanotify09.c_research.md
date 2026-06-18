# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify09.c

Purpose: Regression matrix for events on children when parent, subdirectory, mountpoint, ignored-mask, and reported-name marks interact.

Important APIs/types/functions: `FAN_EVENT_ON_CHILD`, `FAN_ONDIR`, `FAN_CLOSE_NOWRITE`, `FAN_MODIFY`, `FAN_REPORT_DFID_NAME`, `FAN_MARK_IGNORE_SURV`, legacy ignored masks, and multiple fanotify groups.

Control flow: Each testcase creates several groups with first/non-first mark differences, generates close/modify events on files or subdirs, optionally uses reported names, and verifies masks, pids, names, and ignore mask behavior.

State and persistence behavior: State includes several fanotify groups, parent/subdir/mount marks, ignored masks, a mounted filesystem, and event buffers.

Dependencies and integration points: Requires root, a mount device, runtime support for reported-name and ignore-mark features, and regression tags for several kernel commits.

Risks and test signals: The key risk is event merging/masking logic. The test skips unsupported combinations to avoid false failures on older kernels.
