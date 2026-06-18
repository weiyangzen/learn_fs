# File Research: sources/os/plan9/9front/sys/src/cmd/abaco/dat.h

Core Abaco type definitions, UI object model, globals, constants, and function declarations for text/page/window/row/column layout.

Key contents:
- Defines `Runestr`, `Text`, `Line`, `Box`, `Lay`, `Cimage`, `Url`, `Page`, `Window`, `Column`, `Row`, `Exec`, and `Timer`.
- Declares text editing, layout, page loading/rendering, URL, window, column, row, and timer APIs.
- Defines UI constants for scrollbars, margins, borders, tab space, font index calculation, buffer sizes, and stack size.
- Declares global images, fonts, cursors, controllers, row state, selection state, plumbing fds, channels, charset, and webfs mount point.

Role:
- Shared structural contract across the Abaco browser implementation.

Notable risks:
- Many globals couple event handling, rendering, page loading, and selection state.
- `Page` holds both rendered layout and asynchronous loading/refresh state, so lifetime/refcount discipline matters.
