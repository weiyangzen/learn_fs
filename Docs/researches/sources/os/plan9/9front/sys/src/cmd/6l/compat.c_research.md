# File Research: sources/os/plan9/9front/sys/src/cmd/6l/compat.c

- Role: Tiny compatibility include unit for the amd64 linker.
- Includes `l.h` and shared `../cc/compat`.
- This gives 6l access to common Plan 9 compiler compatibility support without duplicating implementation.
