# File Research: sources/local-fs/xfsdump/invutil/screen.c

Provides small ncurses screen helpers.

Functions:
- `put_line()` writes a padded/truncated line to a window with left, center, or right alignment and optional attributes.
- `hitanykey()` prompts in the footer and waits for one keypress.
- `get_string()` prompts on the last line and reads bounded input with echo enabled.

Role:
- Shared rendering/input support for the interactive menu code.

Notable details:
- `put_line()` caps output width to 255 characters and uses a static 256-byte buffer.
- `get_string()` ignores its `win` parameter and always uses `stdscr`.
