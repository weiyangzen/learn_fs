# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-osx/keycodes.h

Macintosh keyboard scan-code and local key-symbol constants for the Carbon/OS X drawterm GUI backend.

Key contents:
- Defines `QZ_*` constants for classic Macintosh physical key codes from Inside Macintosh, including function keys, arrows, keypad keys, modifiers, and iBook-specific keys.
- Defines SDL-like `KEY_*` symbolic ranges for control, cursor, multimedia, keypad, and internal pseudo-keys.
- Provides aliases such as `KEY_BS`, `KEY_DEL`, `KEY_PGUP`, and `KEY_PGDWN`.

Role in this group:
- `gui-osx/screen.c` uses the `QZ_*` constants in `convert_key()` to translate Carbon raw key codes into Plan 9 runes and private keyboard constants from `keyboard.h`.

Notable risks:
- Right-side modifier definitions are disabled because they collide with left-side codes in the old Mac key-code model.
- The table is layout/keyboard-generation sensitive; unusual modern macOS keyboards may not match these historical codes.
