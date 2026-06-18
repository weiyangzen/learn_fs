# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/imainarg.h

Declares argc/argv front-end helpers.

Key points:
- Defines opaque `gs_main_instance` if needed.
- Declares:
  - `gs_main_init_with_args`
  - `gs_main_run_start`
- Notes `argv` should conceptually be `const char *[]`, but ANSI C conventions expose writable strings.

Dependencies and interactions:
- Used by simple Ghostscript program front ends that want command-line behavior.

Research relevance:
- Small high-level API for command-line-compatible interpreter invocation.
