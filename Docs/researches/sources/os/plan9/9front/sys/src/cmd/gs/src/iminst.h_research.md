# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iminst.h

Defines the concrete `gs_main_instance` and library search path structure.

Key points:
- Defines `gs_file_path`:
  - `container`
  - `list`
  - env path
  - final/default path
  - user-specified count
- Defines stdio buffer sizes for stdin/stdout/stderr callouts.
- Defines `gs_main_instance_s` fields:
  - heap allocator
  - memory chunk size
  - name table size
  - run buffer size
  - init stage
  - user error mode
  - current-directory search policy
  - run-start flag
  - library path
  - base time
  - readline data
  - stdio buffers
  - error object
  - display callback
  - current interpreter context
- Defines default init values through `gs_main_instance_default_init_values` and external `gs_main_instance_init_values`.

Dependencies and interactions:
- Used internally by `imain.c` and `imainarg.c`.
- Clients should treat `gs_main_instance` as opaque despite the definition being here.

Research relevance:
- Captures interpreter instance state and lifecycle configuration.
