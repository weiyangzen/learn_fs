# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gs.c

Purpose: Main program entry point for the Ghostscript executable.

Flow: Allocates a `gs_main_instance` using `gs_malloc_init`, initializes it with command-line arguments, optionally runs compile-time `RUN_STRINGS` test strings, then calls `gs_main_run_start`.

Exit mapping: Converts interpreter return codes into process status: success for `0`, `e_Info`, and `e_Quit`; failure for `e_Fatal`; `255` for other errors. It calls `gs_to_exit_with_code` before converting `0/1` to platform `exit_OK/exit_FAILED`.

Dependencies and notes: This is a thin shell around the interpreter API in `imain*` and `iapi.h`; platform exit behavior may still be adjusted by lower-level gp routines.
