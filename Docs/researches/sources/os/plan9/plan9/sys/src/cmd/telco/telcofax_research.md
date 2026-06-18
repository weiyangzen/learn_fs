# File Research: sources/os/plan9/plan9/sys/src/cmd/telco/telcofax

Small rc service script for incoming fax calls.

Key behavior:
- Runs `/bin/aux/faxreceive`.

Notable context:
- `telco.c` execs this as `/bin/service/telcofax` after detecting a fax connection response.
