# File Research: sources/os/bsd/freebsd-src/sbin/camcontrol/progress.h

## Purpose
Declares the progress meter interface used by `camcontrol` operations that need terminal progress reporting.

## Main Elements
- `progress_t`: tracks prefix text, total size, completed units, cached percentage, start/current/ETA times, elapsed time, and terminal width.
- API declarations: `progress_init()`, `progress_update()`, `progress_draw()`, `progress_reset_size()`, and `progress_complete()`.

## Dependencies And Integration
Includes `<sys/types.h>` and `<inttypes.h>`. This is a header-only contract; implementation is elsewhere in `camcontrol`.

## Risk Notes
The state model assumes monotonically advancing work and terminal-width-aware drawing. Callers must keep `size`/`done` coherent to avoid misleading percentages or ETA output.
