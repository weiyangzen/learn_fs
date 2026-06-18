# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/text.c

This file implements Acme’s text/frame behavior: loading, drawing, insertion/deletion, typing, selection, scrolling, completion, and directory display.

Key behavior:
- `textinit()`, `textredraw()`, `textresize()`, and `textclose()` manage frame lifecycle.
- `textload()` loads regular files or directories; directory windows are columnated and sorted.
- `textinsert()`/`textdelete()` update file storage, all shared views, frame display, selections, dirty state, and event streams.
- `texttype()` handles keyboard editing, navigation, scrolling keys, completion, backspace variants, ESC selection, and autoindent.
- `textcommit()` flushes typed cache to the underlying file.
- Selection functions handle normal selection, chording cut/paste, button 2/3 selection, double-click word/bracket matching, and frame scrolling.
- `textshow()`, `textsetorigin()`, and `textbacknl()` keep selections visible.
- `textcomplete()` performs filesystem completion using `complete()` and window-relative paths.
- `textreset()` clears text/file state without building undo records.

Important details:
- Typed characters are cached in each shared `Text` and committed later for efficiency.
- Body edits mark file/window dirty and invalidate UTF read cache.
- Directory windows use a narrower tab width and rebuild columns on resize.
- Multi-view files propagate edits to all views.
- Selection drawing has custom overlap restoration to avoid unnecessary repainting.

Filesystem relevance:
- Very high: loads files/directories, performs filename completion, represents directory listings, and synchronizes display with file-backed buffers.
