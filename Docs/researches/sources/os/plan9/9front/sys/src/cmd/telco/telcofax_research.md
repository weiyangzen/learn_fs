# File Research: sources/os/plan9/9front/sys/src/cmd/telco/telcofax

This is a tiny rc service script for incoming fax calls.

Contents:
- Runs `/bin/aux/faxreceive`.

Integration:
- `telco.c` selects `/bin/service/telcofax` when answering a ring yields fax connection indication `+FCON`.

Risk notes:
- All real fax handling is delegated to `faxreceive`; this script has no local error handling.
