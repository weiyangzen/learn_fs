# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwmain.c

## Role
Win32 GUI executable launcher for Ghostscript. It creates a text window for stdio, loads the Ghostscript API, installs display callbacks, and runs the interpreter.

## Contents
- Defines global instance handle, text-window pointer, `GSDLL` table, Ghostscript instance pointer, and `hwndtext`.
- Implements message polling that dispatches Windows messages and aborts Ghostscript if the text window is closing.
- Redirects Ghostscript stdin/stdout/stderr to the custom text window.
- Implements display-device callbacks that create/delete/update/sync/page image windows through `dwimg.c`.
- Defines `display_callback display` for Ghostscript display device integration.
- `new_main` loads the DLL, creates an instance, optionally initializes the visual tracer under `DEBUG`, sets stdio/poll/display callbacks, injects default display format and resolution arguments, runs `gsapi_init_with_args`, runs `systemdict /start get exec`, exits and deletes the instance, unloads the DLL, and maps Ghostscript error codes to process status.
- `WinMain` parses the command line manually, creates and configures the text window, restores/saves text-window position through registry helpers, runs `new_main`, and keeps the error window open on failure.
- `set_font` reads/writes `gswin32.ini` font settings.

## Important Interfaces
- Entry point `WinMain`.
- Internal Ghostscript runner `new_main`.
- Display callback table `display`.
- Stdio callbacks `gsdll_stdin`, `gsdll_stdout`, `gsdll_stderr`; poll callback `gsdll_poll`.

## Dependencies And Coupling
- Includes Ghostscript API/errors/display headers, visual tracer header, and local Win32 helpers `dwdll`, `dwtext`, `dwimg`, `dwtrace`, `dwreg`.
- Shares image/text window behavior with `dwimg.c` and `dwtext.c`.
- Depends on registry helper values `"Text"` for geometry.

## Risks And Notes
- Manual command-line parser handles quotes but not embedded quotes and uses `MAXCMDTOKENS=128`.
- Allocates `nargv` without checking `malloc` result.
- Uses structured exception handling only for MSVC/Borland stack overflow cases.
- Display size/sync callbacks assume `image_find` succeeds before dereferencing in some paths.

## Filesystem Relevance
Interacts with filenames through command line and drag/drop via text/image windows, but primarily process/UI glue.
