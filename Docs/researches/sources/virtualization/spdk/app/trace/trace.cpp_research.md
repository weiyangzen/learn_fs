# File Research: sources/virtualization/spdk/app/trace/trace.cpp

This file implements `spdk_trace`, a command-line trace display tool. It reads an SPDK trace shared-memory object or saved trace file through `spdk_trace_parser`, then prints events either in the default human-readable format or JSON.

The program supports selecting one lcore (`-c`), printing raw TSC offsets (`-t`), using time deltas between consecutive printed events (`-T`), selecting a shared-memory trace by app name plus shm ID or PID (`-s`, `-i`, `-p`), selecting a trace file (`-f`), and JSON output (`-j`). On Linux, if neither `-s` nor `-f` is provided, it scans `/dev/shm` with `nftw()` and chooses the newest path containing `SPDK_TRACE_SHM_NAME_BASE`.

Default text output prints TSC rate, per-lcore entry counts, then each parsed entry. `print_event()` prints thread name, lcore, event time in microseconds, optional TSC offset, owner description when valid for the event time, tracepoint name, optional size, object ID or object lifetime time, and tracepoint arguments. Argument rendering handles pointer, integer, and string types using tracepoint definitions.

JSON output starts a top-level object containing `tsc_rate`, tracepoint definitions, owner descriptions, and an `entries` array. Each entry includes lcore, tracepoint ID, TSC, optional owner/poller fields, size, object data, related object, and raw argument values. `print_json()` writes JSON output to stdout and aborts on write errors.

The file deliberately avoids linking the full env implementation. It defines `spdk_realloc()`, `spdk_free()`, and `spdk_get_ticks()` in an `extern "C"` block; the first two assert false and the tick function returns zero. A comment explains these exist only because `spdk_util` references env functions that this app does not actually use.

The main validation rules are simple: `-f` and `-s` are mutually exclusive; when using `-s`, either `-i` or `-p` must identify the shm object; lcore selection must not exceed `SPDK_TRACE_MAX_LCORE`. After parsing, the tool initializes the parser in file or shared-memory mode, prints in the selected format, cleans up the parser, and returns the print routine status.
