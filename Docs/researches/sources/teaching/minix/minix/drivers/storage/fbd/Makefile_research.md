# File Research: sources/teaching/minix/minix/drivers/storage/fbd/Makefile

## Purpose
Builds the Faulty Block Device service.

## Key Behavior
- Includes `<bsd.own.mk>`.
- Defines `PROG= fbd`.
- Builds from `fbd.c`, `rule.c`, and `action.c`.
- Links against `libblockdriver` and `libsys`.
- Adds `CPPFLAGS+= -DDEBUG=0`.
- Notes that FBD requires NetBSD libc.
- Includes `<minix.service.mk>`.

## Integration Notes
The source set separates proxy transport, rule storage/matching, and fault actions.

## Risks
Build depends on ioctl definitions from MINIX headers and libc behavior for random-number routines used by actions.
