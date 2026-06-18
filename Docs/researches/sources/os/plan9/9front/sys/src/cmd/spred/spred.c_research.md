# File Research: sources/os/plan9/9front/sys/src/cmd/spred/spred.c

`spred.c` is the main entry point and event loop for the Plan 9 sprite editor.

Key responsibilities:
- Defines global input controllers `mc` and `kc`, plus `quitok`.
- Implements dirty-file quit confirmation in `quit`: first quit with dirty files prints `?` and sets `quitok`; next quit exits.
- Generates right-button menu labels with `menugen`, including actions and open-file entries decorated by `filtitle`.
- Handles the global right-button menu in `rmb`: zerox, close, resize, write, quit, focusing command window, opening file windows, or cycling focus among existing windows.
- Runs the main event loop in `loop`, multiplexing mouse, keyboard, and resize events with `alt`.
- Dispatches left-clicks to window focus/click handling, middle-clicks to active window menu, right-clicks to `rmb`, keyboard runes to active window key handlers, and resize events to `resize`.
- Initializes draw, window system, mouse, keyboard, quote formatting, and enters the loop in `threadmain`.
- Defines `crosscursor`, likely used by window selection/resize logic in adjacent `win.c`.

Important interactions:
- Relies on `initwin`, `winclick`, `resize`, `winzerox`, `winclose`, `winresize`, `newwinsel`, `setfocus`, and active window globals from the window subsystem.
- Command, palette, and sprite behavior is delegated through each window's `Wintab`.
