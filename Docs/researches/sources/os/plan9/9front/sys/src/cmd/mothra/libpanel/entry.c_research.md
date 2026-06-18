# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/entry.c

Implements a single-line text entry widget, including password mode.

Key behavior:
- Stores entry text as Runes with selection/cursor indices.
- Draws clipped text, caret, and selection highlight; password entries display `*`.
- Mouse handling supports focus, selection dragging, snarf/cut/paste chords.
- Keyboard handling supports movement, home/end, clear, line/word erase, backspace, insertion, and submit callback on newline.
- Exposes `plentryval()` as UTF string conversion.

Important dependencies: `keyboard.h`, snarf helpers, draw/font APIs.

Notable risks:
- Password entries suppress snarfing but still store cleartext in memory.
- Reinitialization reallocates existing entry storage through `pl_erealloc`.
