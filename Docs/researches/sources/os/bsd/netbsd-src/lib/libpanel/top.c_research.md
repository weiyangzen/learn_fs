# File Research: sources/os/bsd/netbsd-src/lib/libpanel/top.c

Read completely: 49 lines.

`top_panel` moves a visible panel to the top of the deck. It rejects null and hidden panels, then implements the move as `hide_panel` followed by `show_panel`.

Security/reliability notes: this path touches exposed areas during the hide step even though the panel is immediately reinserted at the top.
