# File Research: sources/local-fs/reiserfsprogs/lib/progbar.c

Implements terminal progress display. `progbar_init()` initializes static bar/space buffers and context state. `progbar_update()` rate-limits updates, computes a 0.1% fixed percent, renders a label, bar, spinner, percent, and optional numeric units, then clears at 100%. Spinner helpers print and clear a rotating `\|/-` character.
