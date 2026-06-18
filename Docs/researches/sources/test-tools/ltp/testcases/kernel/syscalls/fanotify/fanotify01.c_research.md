# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify01.c

Purpose: Checks basic fanotify file events for inode, mount, and filesystem marks, with and without `FAN_REPORT_FID`.

Important APIs/types/functions: `fanotify_init`, `fanotify_mark`, `FAN_ACCESS`, `FAN_MODIFY`, `FAN_CLOSE`, `FAN_OPEN`, ignored-mask flags, `FAN_REPORT_FID`, event metadata parsing, and fd/fid result validation.

Control flow: Each case marks a file, generates open/read/close/write sequences, reads events in batches to prevent unwanted merging, tests ignored masks and `FAN_MARK_IGNORED_SURV_MODIFY`, then verifies event order, masks, pid, and returned fd or `FAN_NOFD` for fid mode.

State and persistence behavior: State includes fanotify groups/marks, ignored masks, a mounted test file, and generated event queues.

Dependencies and integration points: Requires root, a mounted test filesystem, all-filesystems coverage, and runtime support checks for fid, mount, and filesystem marks.

Risks and test signals: Risks are event merging, filesystem support differences, and fid/multi-fs limitations. Failures report missing, unexpected, or malformed events.
