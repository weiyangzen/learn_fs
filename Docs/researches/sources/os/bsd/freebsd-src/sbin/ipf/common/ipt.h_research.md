# File Research: sources/os/bsd/freebsd-src/sbin/ipf/common/ipt.h

## Purpose
Defines a packet-reader abstraction used by IPFilter testing/replay style code.

## Main Elements
- Declares `struct ipread` with callbacks for open, close, and reading an IP packet into an `mb_t`.
- Defines `R_DO_CKSUM` reader flag.
- Includes `<fcntl.h>` and compatibility `__P` handling.

## Dependencies And Integration
Provides a common interface for packet input modules that feed IPFilter-like processing.

## Risk Notes
The callback API depends on `mb_t` being defined by included IPFilter compatibility headers before use.
