# File Research: sources/os/plan9/9front/sys/src/cmd/abaco/wind.c

Abaco window initialization, resizing, lifecycle, locking, tag/status/URL updates, history, and event routing.

Key responsibilities:
- Initializes a window with tag, URL, page area, status text, borders, and button image.
- Resizes window subregions and rerenders pages when page area changes.
- Closes text fields, page contents, URL history, and window storage by refcount.
- Provides `winlock()`/`winunlock()` around window event processing.
- Rebuilds window tags from title, commands, history availability, loading state, and title suffix.
- Updates URL and status text widgets.
- Maintains back/next history and loads history entries.
- Routes mouse/keyboard input to tag/url/status text or page.
- Provides debug dump.

Important behavior:
- `winsettag()` is skipped when the column is unsafe/fullscreen-obscured.
- History truncates forward entries when a new URL is added after going back.
- `wingohist()` increfs the historical URL before loading it.
- `winclean()` currently always returns true, so close prompts are effectively disabled.

Dependencies:
- Uses `Page`, `Text`, `Url`, column safety state, screen drawing, and refcount helpers.

Notable risks:
- Tag rewriting tries to preserve user selection but the preserved-bar logic is mostly disabled.
- Refcounted window lifetime depends on each lock/event/refresh path pairing incref/decref correctly.
