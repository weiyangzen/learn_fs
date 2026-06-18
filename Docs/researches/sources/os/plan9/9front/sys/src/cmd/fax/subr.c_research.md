# File Research: sources/os/plan9/9front/sys/src/cmd/fax/subr.c

## Purpose
Provides logging and error-string helpers for the fax tools.

## Key Elements
Defines global verbose flag, syslog-backed `verbose`, fatal stderr `error`, enum-to-string `seterror`, and receive summary logging in `faxrlog`.

## Dependencies
Uses Plan 9 `syslog`, varargs formatting, and `Modem` error/status fields.

## Behavior/Risks
`seterror` assumes every error enum used has an entry in the static string table. `error` exits immediately and also prints to stdout when verbose is enabled.
