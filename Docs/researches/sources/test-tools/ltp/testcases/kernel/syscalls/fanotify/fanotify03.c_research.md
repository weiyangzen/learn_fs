# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify03.c

Purpose: Validates fanotify permission events and userspace allow/deny responses for inode, mount, filesystem, and parent-child marks.

Important APIs/types/functions: `FAN_OPEN_PERM`, `FAN_ACCESS_PERM`, `FAN_OPEN_EXEC_PERM`, `FAN_ALLOW`, `FAN_DENY`, `struct fanotify_response`, child process generation, and `FAN_CLASS_CONTENT`.

Control flow: Each testcase sets a content-class permission mark, forks a child to open/read/execute targets, reads permission events, verifies masks and pid, writes the configured allow/deny responses, and checks child termination behavior.

State and persistence behavior: State includes a fanotify permission group, response queue, watched file/helper executable, and child process blocked on permission decisions.

Dependencies and integration points: Requires root, mounted test filesystem, resource helper `fanotify_child`, and support checks for permission and exec events.

Risks and test signals: Deadlocks or missed responses are the main risk. The test also gates unsupported filesystem mark and `FAN_OPEN_EXEC_PERM` combinations.
