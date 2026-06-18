# File Research: sources/os/plan9/9front/sys/src/cmd/acme/text.c

This file implements Acme `Text` display, editing, selection, scrolling, completion, loading, and text-view synchronization.

Key responsibilities:
- `textinit()`, `textredraw()`, `textresize()`, and `textclose()` initialize, redraw, resize, and release text frames.
- Directory display:
  - `dircmp()` sorts directory entries.
  - `textcolumnate()` lays directory entries out in tabbed columns.
  - `textload()` loads either regular files or directories, sets file stat metadata, fills frames, handles NUL bytes, and updates all views.
- Text mutation:
  - `textinsert()` and `textdelete()` update the underlying `File` when requested, synchronize all views sharing the file, update frame contents, dirty flags, UTF cache invalidation, scrollbars, and external events.
  - `textbsinsert()` handles backspace characters in inserted streams.
  - `textcommit()` commits typed cache content to the file.
  - `textreadc()` reads from the typing cache or backing buffer.
- Keyboard editing:
  - `texttype()` handles navigation, paging, completion, ESC selection, erase-char/line/word, tab-as-spaces, autoindent, cached typing, and newline commit.
  - `textcomplete()` performs filename completion with `complete()`.
  - `textbswidth()` and helpers calculate erase extents.
- Selection and mouse:
  - `textselect()`, `textselect2()`, `textselect3()`, `textselect23()`, `xselect()`, `textstretchsel()`, and `textclickmatch()` implement click/drag/chord/double-click selection.
  - `framescroll()` and `textframescroll()` support frame-library auto-scroll during selection.
- Visibility:
  - `textshow()`, `textsetselect()`, `selrestore()`, `textbacknl()`, and `textsetorigin()` maintain visible origin and selection drawing.
- `textreset()` resets a text/file display without building undo records.

Important dependencies:
- Uses frame library, draw, completion library, buffer/file/window APIs, scroll drawing, command cut/paste, warning, and path helpers.

Filesystem/storage relevance:
- Primary bridge between loaded files/directories and visible/editable text.
- Directory windows are generated from `dirread()` results.
- Regular files are loaded through `fileload()` and stored in temp-backed buffers.
- External clients observe text insert/delete events through `winevent()` calls.

Notes:
- Typing is cached in each `Text` and committed on newline, ESC, movement, or explicit commit.
- Shared-file views are carefully updated so Zerox windows see consistent edits.
