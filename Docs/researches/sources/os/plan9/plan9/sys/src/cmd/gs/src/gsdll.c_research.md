# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdll.c

## Role

`gsdll.c` implements the deprecated OS/2/Windows Ghostscript DLL API as an adapter over the newer `gsapi` interface in `iapi.h`.

## Main Behavior

It keeps a single global `gs_main_instance *pgs_minst` and global callback `pgsdll_callback`.

Exported functions:

- `gsdll_init(...)` creates a `gsapi` instance, installs stdio and poll callbacks, stores the old callback pointer, and initializes with args.
- `gsdll_execute_begin`, `gsdll_execute_cont`, `gsdll_execute_end` wrap `gsapi_run_string_*`.
- `gsdll_exit` exits and deletes the instance.
- `gsdll_revision` returns product/copyright/revision metadata.

The old callbacks translate `GSDLL_STDIN`, `GSDLL_STDOUT`, and `GSDLL_POLL` events to the caller callback.

## Platform Hooks

Includes Windows or OS/2 headers conditionally. Contains a MacGSView compatibility hack exporting/storing `hwndtext`.

## Dependencies

Uses `iapi.h`, interpreter main-instance internals, Ghostscript revision globals, old `gsdll.h`, and platform DLL calling macros.

## Risks

The file labels the global single-instance state as a hack. It is not reentrant or multi-instance safe. `gsdll_old_stderr` sends `GSDLL_STDOUT` instead of a distinct stderr message, matching the old interface behavior here but surprising for callers expecting stderr separation.
