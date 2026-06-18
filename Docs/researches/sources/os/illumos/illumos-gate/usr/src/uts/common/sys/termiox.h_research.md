# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/termiox.h

## Purpose
Defines the optional extended terminal interface for hardware flow control and clocking modes.

## Main Interfaces
- `NFF`: reserved field count.
- Hardware flow control flags:
  - `RTSXOFF`
  - `CTSXON`
  - `DTRXOFF`
  - `CDXON`
  - `ISXOFF`
- Clock source masks and values:
  - transmit clock `XMTCLK` family
  - receive clock `RCVCLK` family
  - transmitter signal element `TSETCLK` family
  - receiver signal element `RSETCLK` family
- `struct termiox`: hardware flags, clock flags, reserved flags, and spare flags.
- Ioctls:
  - `TCGETX`
  - `TCSETX`
  - `TCSETXW`
  - `TCSETXF`

## Dependencies And Relationships
Used by terminal/serial drivers that implement optional extended hardware flow-control and clocking semantics.

## Research Notes
The comments state that this interface is optional and may not be implemented on all machines.
