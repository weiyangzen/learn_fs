# File Research: sources/os/plan9/9front/sys/src/cmd/upas/send/gateway.c

`gateway()` normalizes the message sender by removing leading systems listed as equivalent to the local host. It calls `skipequiv()` and replaces `mp->sender` only if the returned pointer advanced.

This is used early in `send/main.c` so gatewayed mail does not preserve redundant local routing prefixes.
