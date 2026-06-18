# File Research: sources/teaching/xv6-public/sign.pl

Perl boot-sector signing helper.

Behavior:
- Reads the boot block file.
- Fails if it exceeds 510 bytes.
- Pads it with zero bytes to 510 bytes.
- Appends x86 boot signature bytes `0x55 0xAA`.
- Rewrites the file in place.

Used by the `bootblock` Makefile rule.
