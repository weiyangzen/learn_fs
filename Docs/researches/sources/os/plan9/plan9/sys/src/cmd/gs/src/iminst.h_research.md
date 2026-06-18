# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iminst.h

Defines the concrete `gs_main_instance` and library search path structure.

Key points:
- Defines `gs_file_path` with container/list refs, environment path, final/default path, and user-specified count.
- Defines stdio buffer sizes for stdin/stdout/stderr callouts.
- Defines `gs_main_instance_s` fields for heap allocator, memory chunk size, name table size, run buffer size, init stage, user error mode, current-directory search policy, run-start flag, library path, base time, readline data, stdio buffers, error object, display callback, and current interpreter context.
- Defines default init values and external `gs_main_instance_init_values`.

Research relevance:
- Captures interpreter instance state and lifecycle configuration. Clients should still treat the type as opaque.
