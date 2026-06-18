# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libip/Makefile

Builds `libip.a` for drawterm.

Key content:
- Includes `../Make.config`.
- Archives `eipfmt`, `parseip`, `classmask`, `bo`, and `ipaux` object files.
- Uses standard `$(CC) $(CFLAGS)` compile rule, `$(AR)`, and `$(RANLIB)`.
