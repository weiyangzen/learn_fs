# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iapi.c

Implements the public Ghostscript interpreter embedding API.

Key behavior:
- Maintains a static instance counter with max 1; multiple instances are explicitly unsupported.
- `gsapi_revision` fills product/copyright/revision fields and supports size probing.
- `gsapi_new_instance` initializes malloc memory, allocates a main instance, stores it in `gs_lib_ctx`, installs caller handle, clears callbacks, and returns the library context.
- `gsapi_delete_instance` clears callbacks/display pointer and decrements the counter, but comments note real deletion is not occurring and thread readiness is doubtful.
- Provides setters for stdio callbacks, poll callback, and display callback.
- `gsapi_init_with_args` delegates to `gs_main_init_with_args`.
- Run-string APIs wrap `gs_main_run_string_*`, using the instance’s `error_object`.
- `gsapi_run_file` delegates to `gs_main_run_file`.
- `gsapi_exit` calls `gs_to_exit`.
- `gsapi_set_visual_tracer` installs a global visual tracer pointer.

Research notes:
- The implementation is an embedding facade over `gs_main_instance`.
- The single-instance limitation is enforced in both code and comments.
