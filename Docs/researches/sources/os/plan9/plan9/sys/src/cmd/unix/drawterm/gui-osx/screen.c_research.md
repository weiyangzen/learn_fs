# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-osx/screen.c

Carbon/QuickDraw/Quartz OS X screen, input, cursor, and clipboard backend for drawterm.

Key responsibilities:
- Initializes drawterm as a foreground Carbon application, allocates a full-display-sized 32-bit `Memimage`, wraps it in a `CGImage`, and starts an `osxscreen` kernel process.
- Creates the main window, menu bar, Full Screen command, pasteboard handle, Carbon event handlers, and terminal initialization.
- Translates Carbon keyboard events through `convert_key()` into Plan 9 keyboard runes/constants and sends them to `kbdq`.
- Tracks mouse motion/buttons/wheel events, including Option/Command modifier synthesis for Plan 9 button 2/button 3 behavior.
- Implements full-screen enter/leave via QuickTime `BeginFullScreen`/`EndFullScreen`.
- Implements drawterm screen hooks: `attachscreen`, `flushmemscreen`, `screenload`, `getcolor`, `setcolor`, `mouseset`, `setcursor`, and `cursorarrow`.
- Implements clipboard read/write using the Carbon Pasteboard API with UTF-16 plain text and Plan 9 rune/UTF conversion.

Important behavior:
- `screeninit()` hardcodes 32-bit `XBGR32` screen storage and allocates the backing image at full physical display size, while the window initially occupies 75% of the display.
- `screenload()` creates a subimage from the full backing `CGImage` and draws it into the current window context, flipping the Y coordinate for Quartz drawing.
- Control+Option modifier changes leave full-screen mode.
- Option and Command can synthesize Plan 9 mouse buttons while a button is down, matching X11 drawterm conventions.
- Clipboard read normalizes carriage returns to newlines.

Dependencies:
- Depends on Carbon, QuickTime full-screen APIs, CoreGraphics, Pasteboard, Plan 9 `memdraw`, draw locks, mouse queue state, and keyboard queues.
- Includes `keycodes.h` for Mac raw scan-code mapping.

Notable risks:
- Uses deprecated Carbon, QuickDraw, QuickTime, `SetCursor`, and `InitCursor` APIs.
- `setcolor()` asserts, and palette handling is intentionally absent.
- The backing image size is fixed at initialization; window resizing redraws only within current bounds rather than reallocating the backing store.
- Pasteboard sizing compares UTF-16 byte length against `sizeof rsnarf`; truncation is coarse but bounded.
