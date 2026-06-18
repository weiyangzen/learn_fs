# File Research: sources/os/bsd/netbsd-src/lib/libedit/history.c

## Purpose
Implements libedit's `History`/`HistoryW` API. The file is written as a dual narrow/wide implementation: normal compilation produces wide-character APIs through `chartype.h`, while `historyn.c` defines `NARROWCHAR` and includes this file to produce narrow `char` variants.

## Main Interfaces
- `history_init` / `history_winit`: allocate a `History` object with the built-in linked-list backend.
- `history_end` / `history_wend`: clear and free history state.
- `history` / `history_w`: varargs dispatcher for `H_*` commands.
- Built-in operations include `H_ENTER`, `H_ADD`, `H_APPEND`, `H_DEL`, `H_CLEAR`, navigation, size/unique settings, file load/save, custom backend installation, event data lookup/delete, and replacement.

## Internal Design
The default backend stores entries in a circular doubly linked list with a sentinel header. `history_t` tracks the cursor, maximum retained events, current count, monotonically increasing event IDs, and flags such as `H_UNIQUE`.

Each list node stores a `HistEvent` plus an opaque `data` pointer used by readline compatibility code. New entries are inserted at the front, older entries fall off the tail when `cur > max`, and navigation functions update `cursor`.

The public dispatcher sets `ev` to OK before switching on the requested command. It delegates to function pointers stored in `struct history`, which allows callers to install a custom backend through `H_FUNC`. Size, unique, delete-data, and replacement helpers assume the built-in backend and reject or cast accordingly.

## File Persistence
History files use the cookie `_HiStOrY_V2_\n`. `history_save_fp` writes newest-to-oldest or the requested tail subset using `strvis(..., VIS_WHITE)` after character-set encoding. `history_load` checks the cookie, reads lines with `getline`, decodes with `strunvis`, converts to wide/narrow form, and enters each decoded line.

## Dependencies
Uses `histedit.h` for public command constants/types, `chartype.h` for wide conversion, libc allocation/string APIs, and `<vis.h>` for portable escaped history-file encoding.

## Risks And Notes
- `H_REPLACE` assigns a duplicated replacement string but does not free the old event string in the visible code path, so ownership changes around replacements need care.
- Custom backends bypass default list semantics; operations that require the default backend reject with `_HE_NOT_ALLOWED` except some extension commands that cast `h_ref`.
- The event direction names are historical and easy to confuse: the newest entry is at the list head, while some callers want readline-style offsets from the oldest entry.
