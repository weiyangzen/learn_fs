# File Research: sources/os/bsd/freebsd-src/sbin/route/tests/Makefile

Purpose: test build definition for `sbin/route`.

Behavior:
- Registers shell ATF test `basic`.
- Marks `basic` as exclusive because tests reuse jail names.
- Installs `utils.subr` as a test support file.
- Includes `bsd.test.mk`.

Integration: pairs with `basic.sh`, which relies on VNET jail helper functions and route lookup helpers from `utils.subr`.

Risk notes: tests require root, jails, and `jq`; exclusive metadata prevents parallel jail-name collisions.
