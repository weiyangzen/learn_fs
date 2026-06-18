# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gs.c

Purpose: Defines the Ghostscript executable `main`.

Key interface: `main(int argc, char *argv[])`.

Control flow: allocates a `gs_main_instance` using `gs_malloc_init`, initializes it with command-line arguments, optionally runs compiled test strings when `RUN_STRINGS` is enabled, starts interpretation, maps interpreter status to process exit status, calls `gs_to_exit_with_code`, and returns platform exit constants for success/failure.

Dependencies: Uses interpreter main APIs from `imain*`, `iapi`, `iminst`, error constants, and `gsmalloc`.

Risks and notes: There is no check that `gs_main_alloc_instance` succeeds before use. Exit-code mapping distinguishes normal/info/quit, fatal, and other errors.
