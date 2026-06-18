# File Research: sources/local-fs/xfsprogs/db/text.h

Header for text display support.

Key responsibilities:
- Declares `print_text`.

Dependencies:
- Used by the type registry for `text`, realtime bitmap, and summary display modes.

Notable risks:
- Minimal API depends on global current-buffer state.
