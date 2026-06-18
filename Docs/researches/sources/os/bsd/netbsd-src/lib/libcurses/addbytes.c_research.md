# File Research: sources/os/bsd/netbsd-src/lib/libcurses/addbytes.c

Read completely: 650 lines.

Core byte and wide-character insertion engine for curses output. Public wrappers `addbytes`, `waddbytes`, `mvaddbytes`, and `mvwaddbytes` call `_cursesi_waddbytes()`. `__waddbytes()` lets callers supply attributes.

`_cursesi_waddbytes()` validates the window, tracks cursor pointers and line pointer, and either adds narrow bytes through `_cursesi_addbyte()` or, with `HAVE_WCHAR`, converts multibyte input via `mbrtowc()` and sends `cchar_t` values to `_cursesi_addwchar()`.

`_cursesi_addbyte()` handles tabs, newlines, carriage returns, backspace, pasteol wrapping, scroll-region bottom behavior, attributes/colors/background merging, dirty first/last change pointers, and synchronization. `_cursesi_addwchar()` is the wide-character equivalent with handling for control characters, nonspacing character lists, clearing overwritten continuation cells, line-end width overflow, multi-column continuation cells, wrapping, scrolling, background cells, and dirty ranges.

This is a high-risk implementation file because cursor movement, scroll permission, dirty tracking, background attributes, subwindow offsets, and wide-character cell invariants all interact here.
