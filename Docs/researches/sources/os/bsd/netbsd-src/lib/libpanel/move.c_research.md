# File Research: sources/os/bsd/netbsd-src/lib/libpanel/move.c

Read completely: 58 lines.

`move_panel` moves the associated curses window to a new origin using `mvwin`. If the panel is visible, it touches overlaps at the old location before moving so newly exposed regions are refreshed. Moving to the same coordinates is a no-op success.

Security/reliability notes: direct `mvwin` on a panel’s window would bypass this exposed-area handling; callers should use `move_panel`.
