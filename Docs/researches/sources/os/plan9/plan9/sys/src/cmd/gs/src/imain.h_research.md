# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/imain.h

Declares the front-end API to `imain.c`.

Key points:
- Defines opaque `gs_main_instance`.
- Declares `get_minst_from_memory`, `gs_main_alloc_instance`, `gs_main_init0`, `gs_main_init1`, `gs_main_init2`, library-path helpers, and library file open helper.
- Documents the three initialization stages and common command-line switch equivalents for C API clients.
- Declares execution APIs for files and strings, including suspendable string input.
- Documents return conventions: `0`, `e_Quit`, or `e_Fatal`, with exit code returned separately.
- Declares operand stack push/pop helpers, `gs_main_dump_stack`, and `gs_main_finit`.

Research relevance:
- Top-level API contract for embedding and driving the Ghostscript interpreter.
