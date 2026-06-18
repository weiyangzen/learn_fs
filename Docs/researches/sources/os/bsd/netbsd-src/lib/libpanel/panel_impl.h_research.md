# File Research: sources/os/bsd/netbsd-src/lib/libpanel/panel_impl.h

Read completely: 92 lines.

This private header defines the `struct __panel` layout: associated `WINDOW *`, `char *user`, and TAILQ z-order entry. It declares the global deck and phantom `stdscr` panel, and defines macros for inserting/removing panels, detecting hidden state, and iterating the deck.

Hidden panels are represented by nulling the TAILQ entry’s internal next/prev pointers after removal.

Security/reliability notes: it relies on `<sys/queue.h>` internals to detect unlinked entries, which is intentionally a local implementation detail and not portable outside this queue implementation.
