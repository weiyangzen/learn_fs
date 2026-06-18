# File Research: sources/os/plan9/plan9/sys/src/cmd/trace.c

Graphical scheduler trace viewer for Plan 9 process trace events.

Key responsibilities:
- Optionally enables tracing on supplied process ids by writing `trace 1` to `/proc/<pid>/ctl`.
- Reads binary `Traceevent` records from `/proc/trace` or `-d profdev`.
- Maintains per-task event lists and runtime statistics.
- Opens a draw window, initializes mouse and keyboard controls, and renders a scrolling timeline.
- Displays run/EDF intervals, releases, deadlines, admits, expels, yields, slices, user events, and interrupt markers.
- Supports keyboard controls for reset, pause, zoom in/out, quit, and verbose toggling.
- Supports `-w` new window and `-t triggerproc` pause-on-trigger behavior.

Important behavior:
- Time scales range from sub-millisecond through seconds.
- Per-task height is recalculated on resize unless a fixed new window is managed.
- Runtime intervals are closed when sleep, yield, ready, or slice events arrive.
- Task death frees its event list and compacts the task array.

Notable risks:
- Event history grows with `realloc` per event and is pruned only during redraw.
- Drawing and event ingestion share global mutable state.
- Uses raw binary trace records, so structure ABI must match `trace.h`.
