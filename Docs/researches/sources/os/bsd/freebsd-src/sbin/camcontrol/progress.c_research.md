# File Research: sources/os/bsd/freebsd-src/sbin/camcontrol/progress.c

## Purpose
Provides a terminal progress meter used by `camcontrol` firmware downloads.

## Main Elements
- `progress_init()`: initializes total size, prefix, start time, and terminal width.
- `progress_update()`: updates bytes done, percentage, elapsed time, and ETA.
- `progress_reset_size()`: changes total size.
- `progress_complete()`: updates, draws final state, and prints newline.
- `progress_draw()`: renders carriage-return progress line with percent, bar, abbreviated bytes, throughput, and ETA.

## Dependencies And Integration
Uses `progress.h`, terminal window-size ioctl, time, and direct `write()` to stdout. `fwdownload.c` calls it during firmware chunk transfers.

## Risk Notes
`progress_update()` divides by `prog->size`; callers must initialize with a nonzero total. `progress_init()` duplicates prefix but this module does not free it.
