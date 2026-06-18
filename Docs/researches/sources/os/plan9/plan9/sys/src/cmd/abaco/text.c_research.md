# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/text.c

Editable text buffer and frame interaction layer for Abaco tags, URL fields, status fields, and form inputs.

Key responsibilities:
- Initializes, redraws, resizes, and closes `Text` objects.
- Maintains backing rune storage, frame contents, origin, and selection.
- Inserts/deletes runes and refills the visible frame.
- Implements typing, backspace/delete behavior, tab/newline handling, and selection replacement.
- Implements frame scrolling and visible-range selection.
- Implements primary, secondary, and tertiary mouse selection.
- Supports double-click matching for quotes/brackets/words and newline backing.
- Shows ranges by adjusting origin and selection.
- Dispatches text mouse actions into selection or execute/look behavior.

Dependencies:
- Uses Plan 9 `Frame` API heavily.
- Coordinates with `execute`, `look3`, `putsnarf`, `getsnarf`, scrollbar code, and global selection state.

Notable risks:
- Selection code is intricate and depends on mouse timing/buttons.
- Text buffer edits manually resize rune arrays and must keep frame and logical indices synchronized.
