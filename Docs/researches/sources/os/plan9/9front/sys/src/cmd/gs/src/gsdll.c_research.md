# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdll.c

This file implements the deprecated old Ghostscript DLL interface for OS/2, Windows, and Mac compatibility by forwarding to the newer `iapi.h` API.

Main functions:
- `gsdll_init` creates a `gs_main_instance`, installs stdio and poll callbacks, handles Mac `hwndtext`, stores the legacy global callback, and initializes with args.
- `gsdll_execute_begin`, `gsdll_execute_cont`, and `gsdll_execute_end` wrap `gsapi_run_string_*`.
- `gsdll_exit` exits and deletes the interpreter instance.
- `gsdll_revision` returns product, copyright, revision, and revision date.
- Legacy callback shims translate stdio/poll events into `GSDLL_*` callback messages.

Important constraints:
- It uses a single global `pgs_minst` and global `pgsdll_callback`, explicitly marked as a single-instance hack.
- `e_NeedInput` from `gsapi_run_string_continue` is converted to success for old callers.
- `e_Quit` during initialization maps to `GSDLL_INIT_QUIT`.

This file is compatibility glue, not a native Plan 9 interface.
