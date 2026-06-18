# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/html.c

HTML item sizing, drawing, hit-testing, and flow layout for Abaco.

Key responsibilities:
- Computes sizes for text, rules, images, form fields, buttons, selects, tables, floats, and spacers.
- Draws text, rules, images, form fields, tables, and null boxes.
- Handles link clicks, form submission, radio groups, select widgets, and form keyboard input.
- Creates and initializes layout boxes.
- Maps points to lines/boxes, including table-contained lines.
- Implements line justification, newline creation, item placement, and line fixing.
- Builds a `Lay` tree from libhtml items and renders it.
- Frees layout/table structures.
- Extracts page text into a `Runestr` for snarfing.

Dependencies:
- Uses Plan 9 draw/frame APIs and libhtml item types.
- Calls page navigation/submission helpers, `urlcombine`, `getimage`, `getfont`, `getcolor`, and table helpers from `tabs.c`.

Notable risks:
- HTML layout is custom and stateful; tables, floats, and form controls rely on many geometry invariants.
- Unsupported or incomplete HTML/CSS behavior is expected for this era of browser.
