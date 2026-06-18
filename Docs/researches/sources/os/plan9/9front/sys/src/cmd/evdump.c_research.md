# File Research: sources/os/plan9/9front/sys/src/cmd/evdump.c

This command opens a small draw window and dumps mouse, keyboard, and window-control events. It temporarily remaps keyboard entries to private rune values so it can identify the original layer/keycode/rune mapping on key events.

Key responsibilities:
- Reads `/dev/kbmap`, records mappings, then opens it for writing.
- Installs a note handler to restore the original keyboard map.
- Rewrites mappings to private runes starting at `Kmbase`.
- Opens a new window and initializes draw/mouse.
- Starts keyboard and window-control threads.
- Prints key down/up/repeat, mouse button/position, resize, and window focus/current-state events.

Important implementation notes:
- `k2s` maps many special keyboard runes to symbolic names.
- `wctlproc` restores or reapplies keyboard remapping when the window loses/gains current status.
- `kbproc` compares `/dev/kbd` `k` and `K` records to infer key down/up transitions.
