# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/Makefile

This Makefile builds drawterm's `libauth.a`.

Key contents:
- Includes `../Make.config`.
- Archives auth object files: attribute parsing, challenge/response, proxy, RPC, user/password, and auth attribute support.
- Uses `$(CC) $(CFLAGS)` for `.c` compilation and `$(AR)`/`$(RANLIB)` for archive creation.

Important details:
- `httpauth.c` exists in the directory but is not included in this archive's `OFILES`.
