# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/mothra.c

Implements the main Mothra graphical web browser process. It owns the Plan 9 draw/event/panel UI, page history, command entry, plumbing integration, URL loading workflow, and lifecycle for rendered text/images.

Key responsibilities:
- Defines global UI panels for command entry, message/status label, page list, current URL label, main/alternate text views, and button-3 menu.
- Sets up cursors, fonts, bitmap decorations, event channels, plumb receiver `"web"`, and a process cohort used to kill helper processes on exit.
- Maintains a circular `Www` page log via `www()`/`nwww()` and switches current document with `setcurrent`.
- Handles keyboard scrolling, search, horizontal scroll, mouse wheel-like buttons, panel dispatch, and plumbed URLs in the main event loop.
- Implements command entry behavior: open URL, DuckDuckGo search, reload/go selected URL, jump to history, moth mode, image killing, screenshot dump, save selected hit, and quit.
- Loads URLs through `geturl`: resolves/fetches with `urlget`, determines type from MIME or snooping, pipes HTML through `uhtml`, spawns parsers for HTML/plain text, launches `page -w` for images/documents, and saves unknown types when not plumbed.
- Manages rendered document updates, asynchronous reader completion through `kickpipe`, page image memory pressure via `NPIXMB`, and old-page cleanup.
- Supports “moth mode,” adding/removing hot image-link affordances and allowing image URLs to be selected directly.
- Provides utility functions for status messages, save filters, file descriptor cleanup, shell pipelines, selection URLs, text/image cleanup, hit list writing, snarf/paste, and confirmation.

Important interactions:
- Calls `plrdhtml`/`plrdplain` from `rdhtml.c`, `urlget`/`urlresolve` from `url.c`, MIME snooping from `snoop.c`, image helpers, form helpers, and panel/rtext APIs.
- Relies on `/mnt/web` through URL helpers for HTTP-like fetching, `/dev/label` for window labels, plumbing for external send/receive, and shell tools such as `uhtml`, `page`, `tput`, and `aux/statusmsg`.

Notable quirks:
- Many operations fork helper processes and share state with `RFMEM`; correctness depends on simple flags such as `changed`, `finished`, and `alldone`.
- `geturl` waits before reusing a history slot if a reader is still active.
- Mothra is deliberately permissive and tool-driven rather than a standalone modern browser.
