# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/gateway.c

## Purpose
Gateway sender normalization for `upas/send`.

## Behavior
Calls `skipequiv` on the message sender and, if equivalent local systems are removed, replaces `mp->sender` with the shortened address.

## Dependencies
`skipequiv`, `String`, `message`.

## Risks / Notes
Minimal translation only; broader gateway behavior is handled elsewhere.
