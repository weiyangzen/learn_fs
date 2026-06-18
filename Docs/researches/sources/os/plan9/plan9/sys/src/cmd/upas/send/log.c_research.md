# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/log.c

## Purpose
Syslog logging helpers for delivery, forwarding, and refusal events.

## Main Interfaces
- `logdelivery`
- `loglist`
- `logrefusal`

## Behavior
Unescapes sender/recipient strings, preserves original parent aliases where relevant, logs successful local deliveries, remote/pipe forwarding, and multiline refusals with `error+` continuation prefixes.

## Dependencies
`syslog`, destination list helpers, `String` escaping helpers.

## Risks / Notes
Fields are truncated with `%.256s` to bound log entries.
