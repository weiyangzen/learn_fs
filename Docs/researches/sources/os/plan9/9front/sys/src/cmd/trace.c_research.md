# File Research: sources/os/plan9/9front/sys/src/cmd/trace.c

Read completely: 758 lines, 17892 bytes.

Interactive graphical scheduler trace viewer. It enables tracing for optional pids, reads binary `Traceevent` records from `/proc/trace` or another device, groups events by pid, and draws per-task timelines in a Plan 9 draw window.

Key behavior:
- Flags select trace device, new window, verbose event logging, and trigger process.
- `newtask` creates task rows and names them from `/proc/<pid>/status`.
- `doevent` appends events, calculates run intervals, totals, per-release runtime, and removes dead tasks.
- `redraw` scrolls prior timeline content, draws events, run/EDF spans, interrupts, grid ticks, labels, and elapsed time.
- Keyboard controls reset counters, pause, zoom, quit, and toggle verbose mode.

Dependencies:
- Uses Plan 9 thread/draw/mouse/keyboard APIs, `/proc/trace`, `/proc/<pid>/ctl`, `/dev/wctl`, and `trace.h`.

Reliability notes:
- It asserts event read sizes align to `Traceevent`.
- Task/event arrays are grown with `realloc` and assert success.
