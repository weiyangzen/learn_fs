# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwmainc.c

## Role
Win32 console executable launcher for Ghostscript. It keeps stdio on the console while running display windows on a separate GUI thread.

## Contents
- Provides Ghostscript stdio callbacks backed by `_read`, `fwrite`, and `fflush`.
- Spawns a GUI message thread (`winthread`) because the main thread may block on stdin while Ghostscript runs.
- Uses custom `WM_USER+101` and later messages to ask the GUI thread to open/close/resize/sync/page/poll display windows.
- Implements display callbacks with mutex discipline around image raster access.
- Maintains `first_image` via `image_new`, `image_find`, `image_delete`; posts GUI operations to `thread_id`.
- Initializes DLL/API, optional visual tracer under `DEBUG`, display callback, display format/resolution arguments, and Ghostscript execution.
- Sets console stdin/stdout/stderr modes to binary as appropriate.
- Shuts down the GUI thread by posting `WM_QUIT`.

## Important Interfaces
- Entry point `main`.
- Display callback table `display`.
- GUI thread message handler `winthread`.
- Display callbacks: `display_open`, `display_preclose`, `display_close`, `display_presize`, `display_size`, `display_sync`, `display_page`, `display_update`, `display_separation`.

## Dependencies And Coupling
- Includes Win32, CRT I/O/process headers, Ghostscript API/display/trace headers, and local `dwdll`, `dwimg`, `dwtrace`.
- Paired with `dwimg.c` for image-window implementation.
- Uses `hwndtext = NULL` to signal console mode to image windows.

## Risks And Notes
- `image_new` is dereferenced for mutex creation before checking `img` for null.
- Thread startup wait checks `hthread == INVALID_HANDLE_VALUE`, but `hthread` is a global not initialized to that sentinel in the file.
- Uses `PostThreadMessage`; messages can fail until the thread has created a message queue, hence the explicit retry loop.
- Main and GUI threads rely on correct mutex acquisition/release around image raster pointers.

## Filesystem Relevance
No direct filesystem implementation. Console/drop interactions may pass filenames to Ghostscript.
