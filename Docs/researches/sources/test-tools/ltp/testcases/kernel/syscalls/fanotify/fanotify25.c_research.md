# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify25.c

Purpose: verifies that fanotify mount monitoring works on tracefs and delivers `FAN_MODIFY` events for writes to tracing control files.

Important APIs/types/functions: `tst_fs_type`, tracefs magic `TST_TRACEFS_MAGIC`, `SAFE_MOUNT("tracefs")`, `fanotify_init`, `fanotify_mark` with `FAN_MARK_MOUNT`, `FAN_MODIFY`, `read` on the fanotify fd, and tracefs files such as `/sys/kernel/tracing/kprobe_events`.

Control flow: setup mounts tracefs if needed, checks kprobe events support, creates a nonblocking fanotify group, and marks the tracefs mount for modify events. `run()` forks a child; the child writes a kprobe create command, enables it, disables it, removes it, and after each write drains fanotify events, counting only events from its own pid with `FAN_MODIFY`.

State/persistence behavior: temporarily creates and removes a kprobe event under tracefs. The child is used so tracefs is not kept busy by the main process during cleanup. Cleanup closes the fanotify fd and unmounts tracefs only if this test mounted it.

Dependencies/integration: requires root, `CONFIG_TRACING`, tracefs/kprobe support, and LTP taint checking for warning/die taints.

Risks/test signals: environmental support is the main risk. Passing requires exactly one modify event per tracefs write from the child; wrong masks, read errors other than `EAGAIN`, or missing events fail the test.
