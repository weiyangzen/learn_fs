# File Research: sources/os/plan9/9front/sys/src/cmd/vdiff.c

Purpose: Graphical diff/patch viewer for Plan 9.

Key behavior:
- Parses unified/git-style diff input from files or stdin into patches, file blocks, and typed lines.
- Renders collapsible file blocks with different colors for file headers, hunk separators, additions, deletions, normal lines, and trailing whitespace.
- Supports dark mode (`-b`) and path-component stripping for plumbed edit targets (`-p nstrip`).
- Provides scrollbar, mouse wheel/buttons, keyboard navigation, horizontal panning, expand/collapse menu, and patch-selection menu.
- Right-clicking a diff line plumbs `file:line` to the editor.
- Handles multi-patch input separated by the `⑨` marker and names patches from diff hashes when available.

Dependencies:
- Uses Plan 9 draw, mouse, keyboard, plumb, buffered I/O, and thread APIs.

Notable details:
- Tabs are rendered visibly and trailing spaces are highlighted.
- Long lines are clipped with an ellipsis based on current horizontal pan.
