# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwmain.c

Purpose: Win32 GUI launcher for Ghostscript using `gsdll32.dll`.

Major responsibilities:
- Creates a text window for redirected Ghostscript stdio.
- Loads the Ghostscript DLL and creates a Ghostscript instance.
- Registers stdio, polling, and display callbacks.
- Creates image display windows via `dwimg.c`.
- Determines default display format/resolution from the desktop device context.
- Runs Ghostscript initialization and `systemdict /start get exec`.
- Saves/restores text window size through registry helper functions.

Key parts:
- `poll`: pumps Win32 messages and aborts if the text window is closing.
- `gsdll_stdin/stdout/stderr`: bridge Ghostscript stdio to `TW`.
- Display callback functions: `display_open`, `display_close`, `display_size`, `display_sync`, `display_page`, `display_update`, `display_separation`.
- `new_main`: DLL load, instance lifecycle, display-format argument injection, Ghostscript execution, exit-code mapping.
- `set_font`: reads/writes `gswin32.ini` font settings.
- `WinMain`: command-line parsing, text-window creation, error wait loop, cleanup.

Notes:
- Command-line parser handles quoted spaces but not embedded quotes.
- Uses structured exception handling for stack overflow when compiled with MSVC/Borland.
- Uses old pointer-to-`%x` debug formatting and legacy Win32 APIs.

Filesystem relevance: Runtime file-path handling through command-line and ini/registry settings only.
