# File Research: sources/teaching/xv6-public/vectors.pl

Perl generator for `vectors.S`.

Behavior:
- Emits one global vector label for each interrupt/trap number 0-255.
- Pushes a synthetic zero error code for traps that do not push one in hardware.
- Pushes the trap number and jumps to `alltraps`.
- Emits a `vectors` table of pointers to all vector labels.

Used by the Makefile to generate trap entry assembly consumed by `trap.c`.
