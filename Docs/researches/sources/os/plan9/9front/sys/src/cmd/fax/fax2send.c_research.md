# File Research: sources/os/plan9/9front/sys/src/cmd/fax/fax2send.c

## Purpose
Sends one or more prepared fax page files over a Class 2 fax modem.

## Key Elements
Initializes fax mode, waits for dialing success, enables XON/XOFF flow control, opens each fax file, sends page geometry via `AT+FDT`, DLE-stuffs page data, handles rough flow control and abort characters, sends DLE/ETX, waits for `OK`, sends `AT+FET`, verifies `FPTS`, and cleans up with `AT+FK` on error.

## Dependencies
Uses `openfaxfile`, Bio input, modem I/O helpers, and `Modem` FDCS-derived geometry fields.

## Behavior/Risks
Flow control is deliberately rough and modem-specific. Error cleanup calls `Bterm(m->bp)` even along some paths where open state must be valid. The label name for error cleanup is informal but functionally just abort cleanup.
