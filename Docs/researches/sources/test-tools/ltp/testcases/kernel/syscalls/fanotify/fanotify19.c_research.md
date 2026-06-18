# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify19.c

Purpose: verifies the limited event records delivered to unprivileged fanotify listeners. It checks self-generated and child-generated open/access/modify/close events, both before and after temporarily restoring privileged effective uid before reading.

Important APIs/types/functions: `fanotify_init`, `fanotify_mark`, `FANOTIFY_REQUIRED_USER_INIT_FLAGS`, `FAN_ALL_EVENTS`, `fanotify_event_metadata`, `FAN_EVENT_OK`, `FAN_EVENT_NEXT`, `SAFE_FORK`, `SAFE_WAITPID`, `SAFE_SETEUID`, and `SAFE_GETPWNAM`.

Control flow: `setup()` creates the watched file, makes it writable by unprivileged users, verifies fanotify fid support, and stores the original euid. Each case drops to `nobody`, initializes an unprivileged listener, marks the file, generates events either in the current process or a child, optionally restores root before reading, then scans merged event masks against the expected sequence.

State/persistence behavior: the test mutates the file by reading and writing one byte. Fanotify queue state is consumed once per case. For unprivileged listeners, expected event fds are `FAN_NOFD`; child-originated event pid is expected to be zero.

Dependencies/integration: requires a mounted filesystem, root for setup and credential switching, and the kernel behavior from the tagged unprivileged fanotify change. Child synchronization is simple wait-based rather than checkpoint-based.

Risks/test signals: non-permission events may merge, so the scanner subtracts expected bits from one event. Failures include wrong mask bit, wrong pid visibility, unexpected real fd, premature loop exit, or unsupported unprivileged fanotify.
