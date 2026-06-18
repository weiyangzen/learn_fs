# File Research: sources/os/bsd/netbsd-src/lib/libcurses/ins_wch.c

Implements wide complex-character insertion: `ins_wch`, `mvins_wch`, `mvwins_wch`, and `wins_wch`.

`wins_wch` handles control characters (`\b`, `\r`, `\n`, `\t`), rejects cells that will not fit, shifts complete cells right, clears displaced partial wide cells, writes the new base cell plus non-spacing chain, marks continuation cells with negative `wcols`/`CA_CONTINUATION`, touches the changed line, and calls `__sync`.
