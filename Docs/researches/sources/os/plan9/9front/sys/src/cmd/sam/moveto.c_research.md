# File Research: sources/os/plan9/9front/sys/src/cmd/sam/moveto.c

`moveto.c` handles host-side selection movement, terminal dot notifications, origin selection, and double/triple-click expansion.

`moveto` updates a file's dot range and, if the file is bound to a terminal rasp, sends `Hsetdot`/`Hmoveto` behavior through `telldot` and `outTsl(Hmoveto, ...)`.

`telldot` suppresses redundant dot messages by comparing host dot with terminal-known `tdot`. `tellpat` sends the last regex to the terminal search menu and clears `patset`.

`lookorigin` computes a useful terminal origin near a requested position and line count, scanning backwards up to a bounded character count to avoid pathological long lines.

The file-local `isalnum`, `isspace`, `inmode`, `clickmatch`, `strrune`, and `stretchsel` implement sam's click selection expansion across bracket pairs, quoted strings, newlines, words, and non-whitespace regions.
