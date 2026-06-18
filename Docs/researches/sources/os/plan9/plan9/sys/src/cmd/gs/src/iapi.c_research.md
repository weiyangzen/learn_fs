# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iapi.c

Implements the public Ghostscript interpreter API used by DLL/static clients. It wraps `gs_main_*` interpreter entry points around an opaque library context.

Key behavior:
- `gsapi_revision` returns product/copyright/revision metadata.
- `gsapi_new_instance` allocates memory and a main instance, but gates process-wide instance count to one.
- `gsapi_delete_instance` clears callbacks/display pointer and decrements the counter; comments note no real deletion occurs.
- `gsapi_set_stdio`, `gsapi_set_poll`, and `gsapi_set_display_callback` install callbacks.
- `gsapi_init_with_args`, `gsapi_run_string*`, `gsapi_run_file`, and `gsapi_exit` delegate to `gs_main_*`.
- `gsapi_set_visual_tracer` installs visual tracing interface.

Notable issue: `gsapi_run_string` passes `get_minst_from_memory(ctx->memory)` as the first argument to `gsapi_run_string_with_length`, whose first parameter is expected to be the API instance pointer. This vintage code relies on surrounding context assumptions and is worth scrutiny.
