# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/init.h

Declares daemon lifecycle entry points:
- `init(void)`
- `reinit(void)`

Used by the main daemon/control path to perform initial subsystem setup and config-driven reinitialization.
