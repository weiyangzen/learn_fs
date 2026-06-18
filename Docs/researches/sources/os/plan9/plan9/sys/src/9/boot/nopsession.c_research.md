# File Research: sources/os/plan9/plan9/sys/src/9/boot/nopsession.c

Small 9P `Tnop` session probe helper.

Key behavior:
- Builds a `Fcall` with `NOTAG`, writes it to fd, reads enough bytes for reply header, handles an initial `OK` special case, decodes reply, and validates tag/type.
- `nop(fd)` prints progress and sends `Tnop`.

Used for compatibility/session checks in boot contexts.
