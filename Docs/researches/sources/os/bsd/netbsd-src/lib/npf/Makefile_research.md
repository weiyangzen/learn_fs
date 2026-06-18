# File Research: sources/os/bsd/netbsd-src/lib/npf/Makefile

## Summary
Top-level build dispatcher for NPF extension modules.

## Main Responsibilities
- Includes `bsd.own.mk`.
- Builds `ext_log`, `ext_normalize`, `ext_rndblock`, and `ext_route` only when `${MKPIC} != "no"`.
- Includes `bsd.subdir.mk`.

## Integration Notes
NPF extensions are shared modules and depend on PIC support.
