# File Research: sources/virtualization/nvme-cli/util/dashboard.c

## Role

`dashboard.c` implements the generic live terminal dashboard used by nvme-cli on non-Windows platforms. It owns terminal setup, raw-mode input, resize handling, netlink uevent monitoring, scrollable screen-buffer rendering, and cleanup. The public surface is declared in `dashboard.h`; callers receive a `FILE *` backed by `open_memstream()` and write complete dashboard contents into that stream, then ask this module to render a viewport.

## Main Types And State

- `struct win_frame` records the visible terminal layout: total rows, header offset, data offset, footer offset, and number of visible data rows.
- `struct data_store` records the generated dashboard buffer: `FILE *stream`, dynamic `buf`, `len`, per-row offsets, header/data/footer row counts, scroll start index, and reverse-video row indices.
- `struct dashboard_ctx` combines the data store, frame, refresh interval, remaining sleep interval, uevent fd, terminal fd, original signal mask, and original terminal attributes.

The large in-file comment describes the core model: the data store is the full logical dashboard, while the frame is the current terminal-sized viewport. Header and footer stay pinned; only the data area scrolls.

## Initialization And Cleanup

- `dashboard_init()` allocates and zeroes `dashboard_ctx`, stores the refresh interval, opens the controlling terminal with `ctermid(NULL)`, opens a netlink kobject uevent socket, blocks `SIGWINCH` while recording the current window size, switches the terminal to noncanonical/no-echo mode, creates an `open_memstream()` data stream, hides the cursor, clears the screen, and returns the stream to the caller.
- Error paths unwind in reverse: reset terminal attributes if raw mode was enabled, restore the signal mask, close fds, and free the context.
- `dashboard_exit()` shows the cursor, closes the memstream, frees the memstream buffer and row offset array, restores terminal attributes and the original signal mask, closes terminal and uevent fds, then frees the context.
- `tty_set_raw()` preserves original termios, disables `ICANON` and `ECHO`, sets `VMIN=1`/`VTIME=0`, and applies `TCSAFLUSH`.
- `tty_reset()` restores saved termios and reports failures through `nvme_show_perror()`.

## Event Loop

`dashboard_wait_for_event()` normalizes low-level events into `enum event_type` values:

- timeout at the refresh interval;
- `q` or SIGINT as quit;
- Enter/Return;
- bare Escape;
- up/down arrow escape sequences;
- terminal resize via `SIGWINCH`;
- relevant NVMe-related kernel uevents;
- generic errors.

The lower-level `wait_for_event()` uses `pselect()` over the terminal fd and uevent fd. For ordinary waits it sleeps for the configured interval, adjusted by `rem_interval` when interrupted or awakened by ignored events. For escape-sequence parsing it waits only 1 ms, distinguishing bare Escape from escape-prefix sequences.

Signal handling is integrated with `sighdl-linux.c`: `pselect()` temporarily uses `orig_set`, allowing blocked `SIGWINCH` to be atomically unblocked while waiting. On `EINTR`, it checks `nvme_sigint_received` and `nvme_sigwinch_received`. Resize handling calls `ioctl(TIOCGWINSZ)`, updates `frame.rows`, clears the SIGWINCH flag, and returns `EVENT_TYPE_SIGWINCH`.

Uevents are read from `NETLINK_KOBJECT_UEVENT` with `MSG_DONTWAIT`. The parser scans nul-separated strings looking for `SUBSYSTEM=block`, `DEVNAME=nvme`, `SUBSYSTEM=nvme-subsystem`, or `SUBSYSTEM=nvme`; any match returns `EVENT_TYPE_NVME_UEVENT` so callers can rescan topology.

## Rendering Model

`dashboard_draw_frame()` is the renderer.

For a full redraw (`scroll == 0`):

- flushes the memstream to synchronize `ds->buf` and `ds->len`;
- rewinds the stream so the caller can overwrite from the start on the next generation;
- returns early on an empty buffer;
- null-terminates `ds->buf` at `ds->len`;
- counts newline-terminated rows;
- allocates `row_off[num_rows]` and records the byte offset for each row.

For full redraws and scroll-only redraws:

- reserves `header_rows + footer_rows`;
- computes visible data rows as `frame.rows - reserved`;
- returns without drawing if the terminal is too short for the reserved rows;
- derives data-store data rows as `num_rows - reserved`;
- clamps visible data rows to both the remaining data after `data_start_idx` and the frame capacity;
- computes frame offsets for pinned header/data/footer;
- draws header rows, visible data rows, clears blank data-space rows if the frame has extra space, then draws footer rows.

`draw_line()` moves the cursor with ANSI `\033[%d;1H`, clears the row with `\033[2K`, optionally enables reverse video with `\033[7m`, prints until newline or NUL, then disables reverse video.

## Public Accessors And Mutators

The file provides simple getters/setters for refresh interval, header rows, footer rows, total data rows, current data start index, current frame data rows, and reverse-video markers in header/data/footer sections.

`dashboard_set_data_start()` rejects `off >= ds.data_rows` with `-EINVAL`, otherwise updates the scroll start. It does not reject negative offsets, so callers must avoid passing negative values.

`dashboard_reset()` resets header/footer rows, resets data start to zero, clears reverse markers, flushes the stream, and clears the terminal screen.

## Dependencies

- Linux/POSIX APIs: `termios`, `pselect`, `ioctl(TIOCGWINSZ)`, `NETLINK_KOBJECT_UEVENT`, `socket`, `bind`, `recv`, `open`, `ctermid`, `clock_gettime`.
- Internal APIs: `sighdl.h` signal flags, `common.h` helpers such as `min`, and `nvme-print.h` reporting helpers.
- Built only for non-Windows in `util/meson.build`.

## Notable Edge Cases

- Rows are counted by newline characters. A final line without newline is not counted as a row and may be ignored.
- `ds->data_rows = ds->num_rows - reserved_rows` can become negative if caller-provided header/footer counts exceed generated rows; later offset math assumes a coherent buffer layout.
- `dashboard_reset()` calls `dashboard_set_data_start(ctx, 0)` while `ds.data_rows` can be zero, so the returned `-EINVAL` is intentionally ignored.
- The code assumes ANSI-compatible terminal behavior.
- Netlink uevent parsing assumes messages contain valid nul-separated strings inside the received byte count.

## Research Notes

This file is central to nvme-cli live/dashboard-style commands. It is not a generic curses abstraction; it is a purpose-built ANSI renderer with pinned header/footer sections, scrollable data rows, and refresh/uevent/input integration. Future changes should preserve terminal cleanup on every error path because raw mode and hidden cursor state are process-visible side effects.
