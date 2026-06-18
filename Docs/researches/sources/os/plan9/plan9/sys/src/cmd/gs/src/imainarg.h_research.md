# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/imainarg.h

Declares argc/argv front-end helpers.

Key points:
- Defines opaque `gs_main_instance` if needed.
- Declares `gs_main_init_with_args` and `gs_main_run_start`.
- Notes `argv` should conceptually be `const char *[]`, but ANSI C conventions expose writable strings.

Research relevance:
- Small high-level API for command-line-compatible interpreter invocation.
