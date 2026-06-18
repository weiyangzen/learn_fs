# File Research: sources/os/bsd/netbsd-src/lib/libedit/refresh.c

## Purpose
Implements terminal redisplay for libedit. It builds a virtual display from prompts and the edit buffer, then efficiently updates the physical terminal display.

## Main Interfaces
- `re_putc`, `re_putliteral`: append characters/literals to the virtual display.
- `re_clear_lines`, `re_clear_display`: reset display tracking.
- `re_refresh`: full redraw/update path.
- `re_refresh_cursor`: move only the cursor when possible.
- `re_fastaddc`: optimized append-character refresh.
- `re_goto_bottom`: move cursor to the last used line.

## Rendering Flow
`re_refresh` clears literal storage, resets virtual cursor state, measures the right prompt, prints the left prompt, walks the edited line into `el_vdisplay`, conditionally prints a fitting right prompt, then compares each virtual line against `el_display`.

`re_update_line` computes first/last differences, identifies unchanged middle/end spans worth preserving, and chooses terminal insert/delete/overwrite operations based on terminal capabilities and screen width. It then updates the cached physical display.

## Wide Character Handling
The refresh path accounts for `wcwidth`, multi-column characters, newline wrapping, terminal width, and encoded literal sentinels. Display buffers are padded to terminal width to avoid stale characters affecting cursor movement.

## Dependencies
Uses prompt, terminal capability/output helpers, literal storage, character-type encoding helpers, and `EditLine` display buffers.

## Risks And Notes
- This is a correctness-sensitive terminal state machine; small width-accounting mistakes can cause display corruption.
- Insert/delete optimization depends on `EL_CAN_INSERT` and `EL_CAN_DELETE`.
- Right prompt rendering is only used when it fits on the first visual line with spacing.
