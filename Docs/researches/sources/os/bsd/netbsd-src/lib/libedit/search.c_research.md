# File Research: sources/os/bsd/netbsd-src/lib/libedit/search.c

## Purpose
Implements line and history search utilities for libedit, including glob-style matching, incremental Emacs search, vi search, repeated search, and vi character search.

## Main Interfaces
- `search_init`, `search_end`: allocate/free pattern buffer.
- `el_match`: match strings against wildcard-style patterns.
- `c_hmatch`: test history entries against the active pattern.
- `c_setpat`: update search pattern from the current line.
- `ce_inc_search`: interactive incremental history search.
- `cv_search`: vi `/` and `?` history search.
- `ce_search_line`: search inside the current line.
- `cv_repeat_srch`: repeat vi history search.
- `cv_csearch`: vi `f/F/t/T` character search.

## Control Flow
Incremental search temporarily edits the line buffer to show the search prompt/pattern, reads more keys through `el_wgetc`, updates direction and pattern, searches current line first, falls back to history search commands, and restores the previous history/cursor state on abort or failed search.

Vi search collects a pattern with `c_gets`, stores it in `el_search.patbuf`, and invokes previous/next history search actions. Character search records the last target/direction/till flag for repeat commands.

## Dependencies
Uses history navigation commands, refresh, terminal beep, character-edit word helpers, wildcard matching, and `EditLine` search state.

## Risks And Notes
- Search state is shared across line and history operations through `el_search`.
- Incremental search mutates line/history cursor state and must carefully restore it on abort.
- Optional `ANCHOR` mode changes pattern prefix/suffix behavior.
