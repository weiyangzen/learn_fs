# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspmdrv.c

Implements an OS/2 Presentation Manager display driver/helper for Ghostscript, despite residing in this Plan 9 source tree copy. It can display live shared-memory output from `gsos2.exe` or load a BMP file for display testing.

Key data:
- Global semaphores: `update_event_sem`, `bmp_mutex_sem`.
- `BMAP`: bitmap metadata, palette and old-state tracking.
- `DISPLAY`: display planes, bitcount, palette-manager state.
- `OPTIONS`: saved window origin/size/maximized state.
- Global OS/2 handles: anchor block, frame/client windows, source GS window, update thread.

Key functions:
- `main`: initializes PM, parses `-d id_string` or `-b filename.bmp`, starts update thread, creates window, enters message loop.
- `update_func`: waits on event semaphore and posts `WM_GSUPDATE`.
- `exit_func`: writes profile, closes semaphores, frees shared bitmap memory.
- `find_hwnd_gs`: finds originating CMD/GS window by process ID embedded in ID string.
- `init_window`, `fix_sysmenu`, `restore_window_position`, `read_profile`, `write_profile`.
- `init_display`: opens shared memory, event semaphore, and mutex by generated names.
- `init_bitmap`: loads BMP file into memory and points bitmap info into it.
- `scan_bitmap`: parses `BITMAPINFO`/`BITMAPINFO2`, palette size, dimensions, depth, and data pointer.
- `make_palette`, `make_bitmap`, `paint_bitmap`, `copy_clipboard`.
- `ClientWndProc`: handles paint/update, scrollbars, palette realization, move/size persistence, keyboard navigation, copy/about commands.
- `AboutDlgProc`: handles about dialog dismissal.

Integration:
- Uses OS/2 APIs (`Dos*`, `Win*`, `Gpi*`) plus `gdevpm.h` shared names.
- Synchronizes bitmap access with a mutex while GS may update shared memory.
- Handles OS/2 display-driver quirks with slow/fast bitmap painting paths.

Risk notes:
- Many fixed `char[256]` buffers and `sprintf`/`strcpy` calls predate modern bounds practices.
- `find_hwnd_gs` allocates switch-list memory with `malloc` and does not visibly free it.
- Error strings in `init_display` use `argv[0]`/`argv[1]` in places where generated semaphore/shared-memory names might be more useful.
- Platform-specific and unlikely to build outside OS/2 tooling.
