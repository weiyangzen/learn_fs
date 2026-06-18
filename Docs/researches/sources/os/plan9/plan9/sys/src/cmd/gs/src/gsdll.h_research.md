# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdll.h

## Role

`gsdll.h` declares the deprecated Ghostscript DLL API. It explicitly directs new clients to `API.htm` and `iapi.h`.

## API

Defines callback type `GSDLL_CALLBACK` and global `pgsdll_callback`, callback message constants for stdin/stdout/device/sync/page/resize/poll, and special `gsdll_init` return values.

Exports:

- `gsdll_revision`
- `gsdll_init`
- `gsdll_execute_begin`
- `gsdll_execute_cont`
- `gsdll_execute_end`
- `gsdll_exit`
- `gsdll_lock_device`

Also defines runtime dynamic-linking function pointer typedefs for each exported function.

## Platform Support

Includes `iapi.h`, sets `_Windows` from `__WINDOWS__`, handles IBM C `_System` calling convention, and has MacOS-specific `HWND`/QuickDraw export pragmas.

## Dependencies

Requires DLL export/calling macros from `iapi.h` and platform types such as `HWND`.

## Risks

The API is legacy and global-callback-oriented. `gsdll_lock_device` is declared here but not implemented in `gsdll.c`, so platform/device-specific implementations must provide it or link will fail when referenced.
