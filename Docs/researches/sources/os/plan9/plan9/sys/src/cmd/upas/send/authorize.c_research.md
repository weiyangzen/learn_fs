# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/authorize.c

## Purpose
Runs an authorization command for destinations that match `auth` rewrite rules.

## Behavior
Marks destination authorized, starts the configured process, drains stderr, and if the process exits nonzero changes status to `d_noforward` with stderr as the refusal message.

## Dependencies
`proc_start`, `proc_wait`, `stream`, `dest` status fields.

## Risks / Notes
Authorization command failure is converted into forwarding refusal rather than process-level failure.
