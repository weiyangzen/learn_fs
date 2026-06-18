# File Research: sources/virtualization/guestfs-tools/tests/Makefile.am

Automake file for shared guestfs-tools test support.

Key behavior:
- Distributes `README.txt`.
- Includes shared `subdir-rules.mk`.

Research notes:
- The substantive shared shell helpers are in `functions.sh.in`.
