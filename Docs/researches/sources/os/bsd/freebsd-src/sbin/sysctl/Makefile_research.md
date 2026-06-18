# File Research: sources/os/bsd/freebsd-src/sbin/sysctl/Makefile

## Summary
Builds the `sysctl` runtime utility and installs the default `sysctl.conf` configuration file.

## Main Elements
- Includes `src.opts.mk`.
- Sets `PACKAGE=runtime`.
- Installs `CONFS=sysctl.conf`.
- Builds `PROG=sysctl`, warning level 3, and `sysctl.8`.
- Conditionally enables jail support when `MK_JAIL` is on and not building rescue.
- Links `libjail` when jail support is enabled.
- Enables the `tests` subdirectory when `MK_TESTS` is on.

## Dependencies And Integration
Uses FreeBSD `bsd.prog.mk`; optionally integrates with jail APIs via `-DJAIL` and `libjail`.
