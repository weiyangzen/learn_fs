# File Research: sources/os/bsd/netbsd-src/lib/libpanel/hide.c

Read completely: 56 lines.

`hide_panel` removes a visible panel from the deck. If the panel is already hidden it returns success. After removal, it calls `touchoverlap` for every remaining panel so exposed areas will be repainted by later updates.

Security/reliability notes: hiding does not clear or free the associated window; it only changes deck membership and refresh state.
