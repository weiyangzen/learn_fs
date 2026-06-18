# File Research: sources/os/plan9/plan9/sys/src/cmd/telco/telcodata

Small rc service script for incoming data calls.

Key behavior:
- Prints a message identifying the line as the incoming fax line.
- Asks callers not to make data calls to it.

Notable context:
- `telco.c` execs this as `/bin/service/telcodata` when an answered call appears to be a data call.
