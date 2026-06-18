# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify06.c

Purpose: Regression test for merging ignore masks between inode and mount marks across fanotify priority classes, including overlayfs behavior.

Important APIs/types/functions: `FAN_CLASS_PRE_CONTENT`, `FAN_CLASS_CONTENT`, `FAN_CLASS_NOTIF`, `FAN_MARK_MOUNT`, `FAN_MARK_IGNORED_MASK`, `FAN_MARK_IGNORED_SURV_MODIFY`, `FAN_MODIFY`, and overlay mount helpers.

Control flow: For each scenario, it creates groups across priorities, marks a mount for modify events, adds ignored inode masks to selected groups, generates file modifications, reads event queues, and verifies which groups receive events.

State and persistence behavior: State includes multiple fanotify groups, priority ordering, ignored masks, mounted base/overlay files, and event queues.

Dependencies and integration points: Requires root, mount device support, optional overlayfs, and tags for fanotify/overlay regressions.

Risks and test signals: The risk is subtle event merging or duplicate overlay events. The test closes event fds after verification to avoid descriptor leaks.
