# File Research: sources/os/plan9/9front/sys/src/cmd/acme/look.c

This file implements button-3 look/open behavior, plumbing integration, path expansion, search, and new-file opening.

Key responsibilities:
- `look3()` expands a clicked range, sends events to external clients if they own the window, tries plumber `send`, then falls back to internal open/search.
- `plumblook()` opens files from plumber `showfile` messages and optional address attributes.
- `plumbshow()` creates a new window from plumber `showdata` content.
- `search()` finds a rune string in a text, wrapping once, and shows/selects the match.
- `isfilec()`, `cleanrname()`, `includefile()`, `includename()`, and `dirname()` implement filename/path recognition and normalization.
- `expandfile()` identifies file names and optional Acme addresses around a click.
- `expand()` chooses file or alphanumeric expansion.
- `lookfile()` and `lookid()` locate existing windows by file name or id/dump id.
- `openfile()` opens an existing or new window, loads file content, applies address selection, copies include/indent settings from the originating window, and logs new windows.
- `new()` implements the `New` command over one or more file arguments.

Important dependencies:
- Uses address parser, text buffers, row/column/window logic, plumber, filesystem access (`access`), and file loading.

Filesystem/storage relevance:
- Central to path-to-window resolution, include search, opening files from disk, and plumber-driven file/data display.
- Recognizes `file:addr` syntax and evaluates the address in the target file.

Notes:
- Include lookup searches window include dirs, `/sys/include`, and `/<objtype>/include`.
- Directory-relative expansion derives from the window tag's file name prefix.
