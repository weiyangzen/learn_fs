# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dxmainc.c

## Scope

Console-only Ghostscript shared-library frontend. It runs Ghostscript through `gsapi_*` without a display callback.

## Key Behavior

- Provides stdin/stdout/stderr callbacks using `read`, `fwrite`, and `fflush`.
- Calls `gsapi_new_instance`, `gsapi_set_stdio`, `gsapi_init_with_args`, `gsapi_run_string`, `gsapi_exit`, and `gsapi_delete_instance`.
- Runs the same startup PostScript string as `dxmain.c`: `systemdict /start get exec`.
- Treats `e_Quit` as normal termination and maps `e_Fatal` to process exit code 1, other errors to 255.

## Dependencies

Uses Unix stdio/read APIs and Ghostscript headers `iapi.h` and `ierrors.h`.

## Risks And Invariants

- No GUI or display-device support is installed; graphical output requires another frontend.
- `read` return values are passed directly to Ghostscript, so stdin errors propagate as negative callback returns.
