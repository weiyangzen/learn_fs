# File Research: sources/os/plan9/plan9/sys/src/cmd/page/view.c

Implements the interactive viewer for `page`. It handles window drawing, menus, keyboard/mouse navigation, zoom/fit/rotate, plumbed image additions, page deletion, bitmap export, panning, resize recovery, and new-window setup.

Global state tracks the current document, image, page, rotation angle, screen upper-left placement, and allowed panning range. `showpage` loads through `cachedpage`, optionally resizes the window, and redraws. `redraw` paints image, border, and gray background; `translate` scrolls using differential redraw to minimize work.

Keyboard controls include numeric page selection, next/previous, reverse order, rotate/upside-down, write bitmap, discard, quit, and vertical panning. Mouse controls include left-drag pan, middle command menu, and right page menu. Forward-only documents expose a restricted menu.

Plumbing supports `showdata`, `quit`, absolute paths, and paths relative to the sender’s working directory, adding pages through the document callback. `newwin`, `screenrect`, and `zerox` handle rio/acme window plumbing and spawning a second `page` instance fed by the current image.
