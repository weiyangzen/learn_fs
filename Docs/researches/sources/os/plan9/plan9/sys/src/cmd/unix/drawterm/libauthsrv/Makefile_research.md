# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/Makefile

This Makefile builds drawterm's `libauthsrv.a`.

Key contents:
- Includes `../Make.config`.
- Archives ticket/authenticator conversion files, NVRAM checksum, and password-to-key helpers.
- Uses `$(CC) $(CFLAGS)`, `$(AR)`, and `$(RANLIB)`.

Important details:
- `authdial.c` and `readnvram.c` are present in the directory but not included in this archive's `OFILES`.
