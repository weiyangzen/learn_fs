# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/terminal.py

VTE terminal dialog wrapper used by fsck and cluster config propagation workflows.

Key module behavior:
- Attempts `import vte`.
- Exports:
  - `terminal_ok = False` on import failure.
  - `terminal_ok = True` on success.

Key class:
- `TerminalDialog(gtk.Dialog)`
  - Close button only.
  - Adds title label.
  - Embeds `vte.Terminal`.
  - Sets scrollback to 8192 lines.
  - Adds scrollbar bound to terminal adjustment.

Dependencies:
- PyGTK
- VTE Python bindings

Notable details:
- Modules using terminal workflows gate menu items through `terminal_ok`.
- If `vte` import fails, instantiating `TerminalDialog` would fail because `vte` is undefined, but callers normally check `terminal_ok`.
