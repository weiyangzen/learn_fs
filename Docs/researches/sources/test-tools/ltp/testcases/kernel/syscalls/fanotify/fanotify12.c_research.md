# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify12.c

Purpose: Validates `FAN_OPEN_EXEC` event masks and interactions with ignored masks.

Important APIs/types/functions: `FAN_OPEN`, `FAN_OPEN_EXEC`, `FAN_MARK_IGNORED_MASK`, child `SAFE_OPEN`, child `SAFE_EXECL`, event queue parsing, and resource helper `fanotify_child`.

Control flow: For each case, marks both a regular file and executable helper with the requested mask and optional ignored mask, forks a child that opens the file then execs the helper, reads events, and compares masks/pids to expected sequence.

State and persistence behavior: State is the fanotify group marks, ignored masks, regular file, executable helper, child pid, and event buffer.

Dependencies and integration points: Requires root, fork support, the helper resource file, and runtime support for `FAN_OPEN_EXEC`.

Risks and test signals: The expected combined mask for an exec open is subtle when both `FAN_OPEN` and `FAN_OPEN_EXEC` are requested. Unsupported exec events are skipped.
