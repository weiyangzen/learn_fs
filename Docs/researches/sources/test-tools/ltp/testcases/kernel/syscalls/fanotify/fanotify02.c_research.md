# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify02.c

Purpose: Checks fanotify events on children of a watched directory and behavior after removing `FAN_EVENT_ON_CHILD`.

Important APIs/types/functions: `FAN_EVENT_ON_CHILD`, `FAN_ONDIR`, `FAN_ACCESS`, `FAN_MODIFY`, `FAN_CLOSE`, `FAN_OPEN`, `SAFE_FANOTIFY_INIT`, `SAFE_FANOTIFY_MARK`, and event queue parsing.

Control flow: The test marks the current tmpdir for child events, creates/writes/closes a file, opens/reads/closes it, then removes `FAN_EVENT_ON_CHILD` and verifies a file child no longer generates events while opening the directory itself still does.

State and persistence behavior: State consists of one fanotify group, a tmpdir file, and mark mask changes during the run.

Dependencies and integration points: Requires root and tmpdir isolation, but no mounted external filesystem.

Risks and test signals: The signal is exact event count/order. Event coalescing is controlled by reading the queue between phases.
