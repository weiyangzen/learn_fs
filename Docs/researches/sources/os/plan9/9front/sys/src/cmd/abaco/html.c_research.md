# File Research: sources/os/plan9/9front/sys/src/cmd/abaco/html.c

HTML item sizing, layout, drawing, hit-testing, links, forms, selection extraction, and table recursion for Abaco pages.

Key responsibilities:
- Computes dimensions for text, rules, images, form controls, tables, floats, and spacers.
- Draws text with selection highlighting and underlines, rules, images, form controls, and tables.
- Creates `Box` objects inside `Line` layout rows and assigns draw/mouse/key handlers.
- Implements link clicking with target frame resolution and button-specific behavior.
- Implements form submission, radio/checkbox/select/text field interaction, and form text input.
- Lays out item streams into wrapped lines and nested table layouts.
- Provides line/box hit-testing and `laysnarf()` text extraction from selections.

Important behavior:
- Form text fields lazily allocate embedded `Text` objects and store them in item `aux`.
- Link button 1 loads, button 2 copies URL to status, button 3 sends to plumber.
- Submit builds either query-string GET URL or POST body depending on form method.
- Table and form layout owns nested `Lay` and `Text` cleanup in `layfree()`.

Dependencies:
- Uses libhtml item structs, Abaco page/window utilities, image cache, URL helpers, text editing, and drawing APIs.

Notable risks:
- `boxinit()` tests `if(b->i->anchorid)` rather than `>= 0`, which may skip anchor id 0 while treating negative ids as true unless overridden.
- Selection and layout state are tightly coupled to rectangle coordinates; stale layout after resize/load can affect hit testing.
