# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/screen.c

## Role

`screen.c` implements the VNC server's in-memory screen, console text rendering, cursor rendering, and screen attachment hooks used by `/dev/draw`.

## Screen Setup

- `screeninit()` initializes `memdraw`, allocates `gscreen` with the requested size and channel, creates cursor mask images, builds a cursor color image, initializes a console window, and installs the arrow cursor.
- `screenwin()` draws a simple Plan 9 console area with a title and initializes cursor/text positions.
- `attachscreen()` exposes the `gscreen` `Memdata`, channel, depth, width, rectangle, and softscreen flag to `devdraw.c`.

## Cursor Handling

- `setcursor()` copies cursor bitmaps and increments `cursorver`.
- `cursorrect()` computes the visible cursor rectangle from `cursorpos` and offset.
- `cursordraw()` converts cursor bitmaps into `Memimage` masks and composites cursor set/clear masks onto a destination.
- `cursoron()` tracks current mouse position; `cursoroff()` moves it offscreen.

## Console Rendering

- `screenputs()` decodes UTF-8 fragments, serializes through `drawlock`, calls `screenputc()`, and flushes dirty regions.
- `screenputc()` handles newline, carriage return, tab, backspace, null, and printable runes.
- `scroll()` scrolls the console text area by eight font heights.
- Dirty regions are accumulated in `flushr` and sent through `flushmemscreen()`.

## Notable Limitations And Risk Areas

- `getcolor()` and `setcolor()` are stubs, so colormap operations are effectively inert for this screen implementation.
- Console rendering is basic and primarily supports command output in the private VNC desktop.
- Cursor drawing depends on shared globals from `devmouse.c`.
- `screeninit()` raises compatibility-layer errors rather than returning error codes.
