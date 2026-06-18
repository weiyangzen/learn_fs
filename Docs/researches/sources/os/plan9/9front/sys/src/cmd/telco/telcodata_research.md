# File Research: sources/os/plan9/9front/sys/src/cmd/telco/telcodata

This is a tiny rc service script for incoming modem data calls.

Contents:
- Prints: `This is the plan 9 incoming fax line.`
- Prints: `Please do not make data calls to us.`

Integration:
- `telco.c` selects `/bin/service/telcodata` for answered calls where `ATA` reports a normal data connection rather than fax `+FCON`.

Risk notes:
- It does not interact with the modem stream beyond writing the message.
