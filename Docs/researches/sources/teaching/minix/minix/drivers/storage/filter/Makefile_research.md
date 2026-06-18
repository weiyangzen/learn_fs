# File Research: sources/teaching/minix/minix/drivers/storage/filter/Makefile

## Purpose
Builds the MINIX filter block driver.

## Key Behavior
- Defines `PROG= filter`.
- Builds from `main.c`, `sum.c`, `driver.c`, `util.c`, `crc.c`, and `md5.c`.
- Links against `libblockdriver` and `libsys`.
- Enables debug macros with `CPPFLAGS+= -DDEBUG=1 -DDEBUG2=0`.
- Includes `<minix.service.mk>`.

## Integration Notes
The listed group covers the main, lower-driver, include, CRC, and MD5 pieces; `sum.c` and `util.c` are also part of this binary and supply checksum layout and helper allocation/alarm behavior.

## Risks
Debug defaults affect console noise and potentially timing-sensitive behavior in a storage proxy.
