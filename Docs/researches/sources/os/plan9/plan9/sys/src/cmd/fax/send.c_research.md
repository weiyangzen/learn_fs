# File Research: sources/os/plan9/plan9/sys/src/cmd/fax/send.c

Command-line entry point for sending fax page files.

Key behavior:
- Parses `-v`.
- Requires a phone number and at least one page file.
- Builds a telco address with `netmkaddr(number, "telco", "fax!9600")`.
- Dials the modem service, initializes `Modem`, and calls `faxsend()`.
- Logs success or failure to syslog category `fax`.

Important implementation details:
- The modem data fd and control fd come from `dial()`.
- On send failure, prints the modem error and exits with that error string so queue systems can retry based on status.

Risks and invariants:
- Assumes the telco service and fax modem are available through Plan 9 networking.
