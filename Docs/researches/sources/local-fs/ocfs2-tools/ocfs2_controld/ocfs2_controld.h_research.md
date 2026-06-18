# File Research: sources/local-fs/ocfs2-tools/ocfs2_controld/ocfs2_controld.h

This header is the internal interface for `ocfs2_controld`. It declares shared globals, logging macros, subsystem entry points, stack abstraction functions, checkpoint APIs, CPG APIs, DLM control APIs, mount APIs, and retry/backoff helpers.

`log_debug` writes to the in-memory daemon dump buffer and optionally stderr; `log_error` also syslogs. `retry_warning` logs on power-of-two retry counts using a local hweight helper.

The header is central glue for daemon modules and stack-specific adapters. Its global state and macro logging model tightly couple all daemon source files.
