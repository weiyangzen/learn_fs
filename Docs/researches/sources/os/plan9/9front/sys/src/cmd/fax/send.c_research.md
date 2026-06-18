# File Research: sources/os/plan9/9front/sys/src/cmd/fax/send.c

## Purpose
Command entry point for dialing and sending fax page files.

## Key Elements
Parses `-v`, requires a number and at least one page, dials the number through `telco` service `fax!9600`, initializes the `Modem`, invokes `faxsend`, prints/logs failure or success, and exits with an appropriate status.

## Dependencies
Uses Plan 9 networking `netmkaddr`/`dial`, syslog, and the fax send stack.

## Behavior/Risks
Dial failure exits with a retry-oriented message. Success/failure syslog formatting references the remaining `argv` after the number has been consumed, so logged page names depend on caller arguments.
