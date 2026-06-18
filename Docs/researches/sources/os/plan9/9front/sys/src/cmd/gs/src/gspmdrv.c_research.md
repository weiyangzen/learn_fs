# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gspmdrv.c

Implements the OS/2 Presentation Manager display driver helper program for Ghostscript.

Main responsibilities:
- Runs as `gspmdrv -d id_string` to display a bitmap produced by Ghostscript through shared memory and semaphores.
- Runs as `gspmdrv -b filename.bmp` to display a BMP file for testing.
- Creates an OS/2 PM frame/client window, message queue, update thread, scroll bars, palette support, and system-menu additions.
- Reads and writes window position/size/maximized state to the OS/2 user profile.
- Uses named shared memory for bitmap data, named event semaphore for update notification, and named mutex semaphore for bitmap synchronization.
- Scans old `BITMAPINFO` and newer `BITMAPINFOHEADER2` layouts.
- Handles palette-manager setup for 8-bit bitmaps.
- Paints bitmap regions via `GpiDrawBits`, with fallback/double-buffer paths for known OS/2 display-driver bugs.
- Supports clipboard copy as `CF_BITMAP`.
- Handles scrolling, resizing, keyboard navigation, repaint, palette realization, and an About dialog.

Filesystem relevance is indirect: this is a platform UI/display helper within the vendored Ghostscript source tree, not filesystem code.
