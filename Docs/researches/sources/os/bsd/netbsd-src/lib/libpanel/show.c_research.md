# File Research: sources/os/bsd/netbsd-src/lib/libpanel/show.c

Read completely: 47 lines.

`show_panel` makes a hidden panel visible by inserting it at the top of the deck. It rejects null panels and already-visible panels.

Security/reliability notes: unlike some ncurses behavior, this implementation separates `show_panel` for hidden panels from `top_panel` for visible panels.
