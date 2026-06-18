# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/edit.c

Implements a multi-line editable text panel on top of `Textwin`.

Key behavior:
- Lazily creates a `Textwin`, reshapes/redraws it, and updates vertical scrollbars.
- Supports snarf/paste, mouse selection, cut/paste chord handling, scrolling, and keyboard editing.
- Keyboard commands handle clear, backspace, line erase, word erase, and normal Rune insertion.
- Exposes edit APIs: scroll, get text/length/selection, set selection, paste, and move.

Important dependencies: `textwin.c`, `snarf.c`, `keyboard.h`, libpanel scroll callbacks.

Notable risks:
- Selection indices initialize to `-1`; callers rely on drawing/interaction to establish sensible values.
- Editing redraws through `Textwin`, whose replacement code has a documented incomplete optimized path.
