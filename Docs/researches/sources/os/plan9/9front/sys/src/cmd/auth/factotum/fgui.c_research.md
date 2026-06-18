# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/fgui.c

Graphical factotum helper for confirmation prompts and missing-key entry.

Key responsibilities:
- Opens `/mnt/factotum/confirm` and `/mnt/factotum/needkey`, reads request messages, and serializes them through a main UI loop.
- Displays key-use confirmation windows with Accept/Refuse and optional remember behavior.
- Caches remembered confirmation answers by matching attribute sets.
- Displays needkey entry forms for queried attributes, masking private fields with an invisible font.
- Writes newly entered keys to `/mnt/factotum/ctl`.
- Writes completion, denial, or cancellation responses back to the relevant factotum file.
- Hides the window while idle and unhides it for active prompts.

Dependencies:
- Uses Plan 9 draw/mouse/keyboard/control libraries, factotum attribute formatting/parsing, and `/mnt/factotum` control files.

Notable risks:
- Remembered confirmations are in-memory only.
- Needkey form construction mutates the parsed attribute list to add blank query fields.
