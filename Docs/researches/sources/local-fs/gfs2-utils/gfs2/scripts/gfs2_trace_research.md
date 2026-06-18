# File Research: sources/local-fs/gfs2-utils/gfs2/scripts/gfs2_trace

Python tool for listing, enabling, disabling, and capturing GFS2 ftrace trace events.

Main classes:
- `FileUtils`: static file read/write helpers.
- `TraceEvent`: wraps one trace event directory and reads/writes `enable`, reads `filter`, `format`, and `id`.
- `TraceEvents`: discovers all event directories under `/sys/kernel/debug/tracing/events/gfs2`.

Default paths:
- Debugfs: `/sys/kernel/debug`
- GFS2 trace events: `/sys/kernel/debug/tracing/events/gfs2`
- Trace pipe: `/sys/kernel/debug/tracing/trace_pipe`
- PID file: `/var/run/<script>.pid`

CLI supports:
- `-l`: list event enable states.
- `-E`: enable all GFS2 trace events.
- `-e`: enable selected comma-separated events.
- `-N`: disable all.
- `-n`: disable selected comma-separated events.
- `-c`: capture `trace_pipe` output to a file, then archive it as `.tar.bz2`.
- `-d`, `-q`: debug/quiet logging.

Behavioral flow:
1. Parse options and configure logger.
2. Create PID file, refusing concurrent execution.
3. Require at least one mounted GFS2 filesystem from `/proc/mounts`.
4. Mount debugfs if not already mounted.
5. Discover trace event directories.
6. Optionally list current states.
7. Apply all-event and selected-event enable/disable operations.
8. If capture requested, read `trace_pipe` until EOF or Ctrl-C, write output file, then bzip2 tar it.
9. Remove PID file and exit.

Research notes:
- The script writes directly to kernel tracing control files and therefore needs suitable privileges.
- `TraceEvent.setEventEnable` only accepts `"0"` or `"1"`.
- `ExtendOption` here correctly appends each split comma value.
