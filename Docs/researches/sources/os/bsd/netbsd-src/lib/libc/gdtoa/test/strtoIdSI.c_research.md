# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/strtoIdSI.c

Two-line sudden-underflow wrapper:
- Defines `Sudden_Underflow`.
- Includes `../strtoId.c`.

Purpose: compile the double interval converter under sudden-underflow semantics for comparison tests.
