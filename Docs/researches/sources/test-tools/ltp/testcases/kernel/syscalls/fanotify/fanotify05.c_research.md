# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify05.c

Purpose: Checks that queue overflow produces `FAN_Q_OVERFLOW` for limited queues and not for unlimited queues.

Important APIs/types/functions: `FAN_UNLIMITED_QUEUE`, `FAN_REPORT_FD_ERROR`, `FAN_Q_OVERFLOW`, `/proc/sys/fs/fanotify/max_queued_events`, `SAFE_OPEN`, and nonblocking fanotify reads.

Control flow: The test determines the queue limit, marks a mount for `FAN_OPEN`, generates more open events than the queue can hold without reading, then drains events and counts regular open versus overflow records.

State and persistence behavior: State is a fanotify event queue under pressure plus many generated files on a mounted test filesystem.

Dependencies and integration points: Requires root, mounted filesystem, and support checks for `FAN_REPORT_FD_ERROR`.

Risks and test signals: Overflow tests are sensitive to kernel queue sizing and event generation count. The expected fd for overflow differs when `FAN_REPORT_FD_ERROR` is enabled.
