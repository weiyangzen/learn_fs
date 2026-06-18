# File Research: sources/os/bsd/netbsd-src/lib/libpanel/hidden.c

Read completely: 45 lines.

`panel_hidden` returns `ERR` for a null panel, `TRUE` when the panel is not linked into the deck, and `FALSE` otherwise.

Security/reliability notes: hidden state is inferred from internal TAILQ link pointers.
