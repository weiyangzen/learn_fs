# File Research: sources/os/plan9/plan9/sys/src/9/port/devmouse.c

Implements `#m`, the mouse/cursor device. The namespace contains `cursor`, `mouse`, `mousein`, and `mousectl`.

`Mouseinfo` tracks current position/buttons/time/counter, accumulated deltas, redraw flag, resize generation, one-reader open state, acceleration settings, and a circular queue for button-change events. `Cursorinfo` and `curs` hold the active cursor.

`mouse` reads block until movement/button/resize state changes, then return Plan 9 mouse records (`m...`) or resize records (`r...`). Button states pass through configurable `buttonmap`, and scroll buttons can be swapped. `cursor` reads/writes the binary cursor shape. `mousein` is privileged and injects absolute position/button/time events. Writing `mouse` moves cursor position. `mousectl` supports `swap`, `scrollswap`, `buttonmap`, plus platform-specific `mousectl` passthrough.

`mousetrack` is the interrupt-level update path. It applies acceleration, clamps to screen clip rectangle, merges keyboard-emulated buttons, queues button changes, wakes readers, marks cursor redraw, and records screen activity. `mouseclock` periodically applies accumulated deltas, redraws cursor, and checks draw idle blanking.

The file also contains serial mouse protocol decoders for Microsoft 3-button, IntelliMouse with scroll, and Logitech 5-byte formats. They resynchronize after idle gaps and translate packets into `mousetrack` calls.

Dependencies include draw/screen cursor hooks, global framebuffer state, keyboard mouse emulation, and monitor configuration. The device enforces exclusive `mouse` reader semantics.
